from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.views.generic import View

from entries.models import Competition, SessionRound
from entries.views import TargetListView

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
        return render(request, self.template, locals())

input_scores = login_required(InputScoresView.as_view())

class InputArrowsView(View):
    template = 'input_arrows.html'

    def get(self, request, slug, round_id, dozen, boss):
        return render(request, self.template, locals())

input_arrows = login_required(InputArrowsView.as_view())
