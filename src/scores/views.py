from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import View

from entries.models import Competition, SessionRound
from entries.views import TargetListView

from scores.forms import get_arrow_formset
from scores.models import Score

from itertools import groupby

class InputScoresView(TargetListView):
    template = 'input_scores.html'

    def get(self, request, slug):
        competition = get_object_or_404(Competition, slug=slug)
        session_rounds = SessionRound.objects.filter(session__competition=competition).order_by('session__start')
        scores = [
            (
                session_round.session,
                session_round,
                Score.objects.boss_groups(session_round),
            )
            for session_round in session_rounds
        ]
        sessions = []
        for key, values in groupby(scores, lambda x: x[0]):
            sessions.append((key, [value[1] for value in values]))
        focus = request.GET.get('fd', '') + '-' + request.GET.get('ft', '')
        return render(request, self.template, locals())

input_scores = login_required(InputScoresView.as_view())

class InputArrowsView(View):
    template = 'input_arrows.html'

    def get(self, request, slug, round_id, boss, dozen):
        competition = get_object_or_404(Competition, slug=slug)
        forms = get_arrow_formset(round_id, boss, dozen)
        return render(request, self.template, locals())

    def post(self, request, slug, round_id, boss, dozen):
        competition = get_object_or_404(Competition, slug=slug)
        forms = get_arrow_formset(round_id, boss, dozen, data=request.POST)
        arrows = []
        failed = False
        for score in forms:
            for form in score['forms']:
                if form.is_valid():
                    arrows.append(form.save(commit=False))
                else:
                    print form.errors
                    failed = True
        if not failed:
            for arrow in arrows:
                arrow.save()
            return HttpResponseRedirect(reverse(input_scores, kwargs={'slug': slug}) + '?fd={0}&ft={1}#session-{3}-round-{2}'.format(dozen, boss, round_id, SessionRound.objects.get(pk=round_id).session.pk))
        return render(request, self.template, locals())

input_arrows = login_required(InputArrowsView.as_view())
