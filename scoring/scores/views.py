from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import View

from reportlab.platypus import PageBreak, Table

from entries.models import Competition, SessionRound
from entries.views import TargetList, HeadedPdfView

from scores.forms import get_arrow_formset
from scores.models import Score

from itertools import groupby

class InputScoresView(TargetList):
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
        if 'ft' in request.GET and 'fd' in request.GET:
            focus = request.GET['fd'] + '-' + request.GET['ft']
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
                    failed = True
        if not failed:
            for arrow in arrows:
                arrow.save()
            return HttpResponseRedirect(reverse(input_scores, kwargs={'slug': slug}) + '?fd={0}&ft={1}#session-{3}-round-{2}'.format(dozen, boss, round_id, SessionRound.objects.get(pk=round_id).session.pk))
        return render(request, self.template, locals())

input_arrows = login_required(InputArrowsView.as_view())

class LeaderboardView(View):
    template = 'leaderboard.html'
    title = 'Leaderboard'
    leaderboard = True

    def get_results(self):
        session_rounds = SessionRound.objects.filter(session__competition=self.competition).order_by('session__start')
        scores = [
            (
                session_round.session,
                session_round,
                Score.objects.results(session_round, leaderboard=self.leaderboard),
            )
            for session_round in session_rounds
        ]
        sessions = []
        for key, values in groupby(scores, lambda x: x[0]):
            sessions.append((key, [value[1] for value in values]))
        return session_rounds, scores, sessions

    def get_context(self, request, slug):
        competition = self.competition = get_object_or_404(Competition, slug=slug)
        session_rounds, scores, sessions = self.get_results()
        title = self.title
        return locals()

    def get(self, request, *args, **kwargs):
        context = self.get_context(request, *args, **kwargs)
        return render(request, self.template, context)

leaderboard = login_required(LeaderboardView.as_view())

class LeaderboardBigScreen(LeaderboardView):
    template = 'leaderboard_big_screen.html'

leaderboard_big_screen = login_required(LeaderboardBigScreen.as_view())

class ResultsView(LeaderboardView):
    leaderboard = False # FIXME: set this back to True when leaderboard has been made more efficient! The massive counted annotate is slooooow.
    title = 'Results'

results = login_required(ResultsView.as_view())

class ResultsPdf(HeadedPdfView, ResultsView):
    title = 'Results' # because ResultsView is a mixin, its attrs are not used.

    def update_style(self):
        self.styles['h1'].alignment = 1
        self.styles['h2'].alignment = 1

    def row_from_entry(self, entries, entry):
        row = [
            entries.index(entry) + 1 if not entry.disqualified else None,
            entry.target.session_entry.competition_entry.archer.name,
            entry.target.session_entry.competition_entry.club.name,
        ]
        # TODO: Denormalise this (or something!)
        subrounds = entry.target.session_entry.session_round.shot_round.subrounds
        if subrounds.count() > 1:
            if entry.disqualified:
                row += [None] * 4
            else:
                # Arrow of round has been stored off by a dozen
                counter = 13
                subround_scores = []
                for subround in subrounds.order_by('-distance'):
                    subround_scores.append(entry.arrow_set.filter(arrow_of_round__in=range(counter, counter + subround.arrows)).aggregate(Sum('arrow_value'))['arrow_value__sum'])
                    counter += subround.arrows

                row += subround_scores

        row += [
            entry.score if not entry.disqualified else 'DSQ',
            entry.golds if not entry.disqualified else None,
            entry.xs if not entry.disqualified else None,
        ]
        return row

    def get_elements(self):
        elements = []

        session_rounds, scores, sessions = self.get_results()
        for session, session_round, results in scores:
            elements.append(self.Para(session_round.shot_round, 'h1'))

            for category, entries in results:
                elements.append(self.Para(category , 'h2'))
                table = Table([self.row_from_entry(entries, entry) for entry in entries])
                elements.append(table)
            
            elements.append(PageBreak())

        return elements

results_pdf = login_required(ResultsPdf.as_view())
