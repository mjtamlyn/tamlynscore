from itertools import groupby
import math

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import View, ListView

from reportlab.platypus import PageBreak, Table

from entries.models import Competition, SessionRound
from entries.views import TargetList, HeadedPdfView, BetterTargetList

from scores.forms import get_arrow_formset
from scores.models import Score, Arrow

from utils import class_view_decorator


@class_view_decorator(login_required)
class InputScores(BetterTargetList):
    template_name = 'scores/input_scores.html'

    def get_queryset(self):
        return super(InputScores, self).get_queryset().order_by('session_entry__session_round__session', 'boss', 'target')

    def add_unallocated_entries(self, target_list):
        pass

    def get_context_data(self, **kwargs):
        context = super(InputScores, self).get_context_data(**kwargs)

        for allocation in self.allocations.filter(score__isnull=True):
            Score.objects.create(target=allocation)

        arrows = Arrow.objects.filter(score__target__in=self.allocations).select_related('score__target')
        target_lookup = {}
        for arrow in arrows:
            target = arrow.score.target
            if target not in target_lookup:
                target_lookup[target] = {}
            dozen = math.floor((arrow.arrow_of_round - 1) / 12)
            dozen = int(dozen)
            if dozen not in target_lookup[target]:
                target_lookup[target][dozen] = []
            target_lookup[target][dozen].append(arrow)

        for session in context['target_list']:
            for session_round, options in context['target_list'][session].iteritems():
                targets = options['targets']
                bosses = options['bosses'] = []
                for boss, allocations in groupby(targets, lambda t: t.boss):
                    combined_lookup = {}
                    allocations = list(allocations)
                    for dozen in session_round.shot_round.iter_dozens():
                        combined_lookup[dozen] = True
                        for allocation in allocations:
                            if (allocation not in target_lookup
                                    or dozen not in target_lookup[allocation]
                                    or not len(target_lookup[allocation][dozen]) == 12):
                                combined_lookup[dozen] = False
                    bosses.append((boss, combined_lookup))

        if 'ft' in self.request.GET and 'fd' in self.request.GET:
            context['focus'] = self.request.GET['fd'] + '-' + self.request.GET['ft']

        return context


class InputArrowsView(View):
    template = 'input_arrows.html'

    def get(self, request, slug, round_id, boss, dozen):
        competition = get_object_or_404(Competition, slug=slug)
        scores = Score.objects.filter(target__session_entry__session_round=round_id, target__boss=boss).order_by('target__target').select_related()
        forms = get_arrow_formset(scores, round_id, boss, dozen)
        return render(request, self.template, locals())

    def post(self, request, slug, round_id, boss, dozen):
        competition = get_object_or_404(Competition, slug=slug)
        scores = Score.objects.filter(target__session_entry__session_round=round_id, target__boss=boss).order_by('target__target').select_related()
        forms = get_arrow_formset(scores, round_id, boss, dozen, data=request.POST)
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
            for score in scores:
                score.update_score()
                score.save(force_update=True)
            return HttpResponseRedirect(reverse('input_scores', kwargs={'slug': slug}) + '?fd={0}&ft={1}#session-{3}-round-{2}'.format(dozen, boss, round_id, SessionRound.objects.get(pk=round_id).session.pk))
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


@class_view_decorator(login_required)
class LeaderboardCombined(ListView):
    template_name = 'scores/leaderboard_combined.html'
    title = 'Leaderboard (all archers)'

    def get_queryset(self):
        scores = Score.objects.filter(target__session_entry__competition_entry__competition__slug=self.kwargs['slug']).select_related().order_by(
                'target__session_entry__competition_entry__bowstyle',
                'target__session_entry__competition_entry__archer__gender',
                'disqualified',
                '-score', 
                '-golds', 
                '-xs'
        )
        return scores

    def get_context_data(self, **kwargs):
        context = super(LeaderboardCombined, self).get_context_data(**kwargs)
        scores = context['object_list']
        if scores:
            competition = scores[0].target.session_entry.competition_entry.competition
        else:
            competition = Competition.objects.get(slug=self.kwargs['slug'])
        context['competition'] = competition
        context['title'] = self.title

        results = []
        for category, scores in groupby(scores, lambda s: s.target.session_entry.competition_entry.category()):
            results.append((category, list(scores)))
        context['results'] = results
        return context


@class_view_decorator(login_required)
class LeaderboardCombinedNovice(LeaderboardCombined):
    title = 'Leaderboard (Novice)'

    def get_queryset(self):
        scores = super(LeaderboardCombinedNovice, self).get_queryset()
        scores = scores.filter(target__session_entry__competition_entry__novice='N')
        return scores


@class_view_decorator(login_required)
class LeaderboardTeams(ListView):
    template_name = 'scores/leaderboard_teams.html'
    title = 'Leaderboard (Teams)'

    def get_queryset(self):
        scores = Score.objects.filter(target__session_entry__competition_entry__competition__slug=self.kwargs['slug']).select_related().exclude(target__session_entry__competition_entry__bowstyle__name='Compound')
        scores = scores.order_by(
                'target__session_entry__competition_entry__bowstyle',
                'target__session_entry__competition_entry__archer__gender',
                'disqualified',
                '-score',
                '-golds',
                '-xs'
        )
        return scores

    def get_club_results(self, scores):
        club_results = {}
        for score in scores:
            club = score.target.session_entry.competition_entry.club
            if club not in club_results:
                club_results[club] = []
            club_results[club].append(score)
        for club, scores in club_results.iteritems():
            team = sorted(scores, key=lambda s: (s.score, s.hits, s.golds), reverse=True)[:4]
            total = sum([s.score for s in team])
            club_results[club] = {'team': team, 'total': total, 'club': club}
        club_results = sorted(club_results.values(), key=lambda s: s['total'], reverse=True)
        return club_results

    def get_context_data(self, **kwargs):
        context = super(LeaderboardTeams, self).get_context_data(**kwargs)
        scores = context['object_list']
        if scores:
            competition = scores[0].target.session_entry.competition_entry.competition
        else:
            competition = Competition.objects.get(slug=self.kwargs['slug'])
        context['competition'] = competition
        context['title'] = 'Leaderboard'

        context['club_results'] = self.get_club_results(scores)
        novice_scores = scores.filter(target__session_entry__competition_entry__novice='N')
        context['novice_results'] = self.get_club_results(novice_scores)

        context['title'] = self.title

        return context


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
                    subround_scores.append(entry.arrow_set.filter(arrow_of_round__in=range(counter, counter + subround.arrows)).aggregate(models.Sum('arrow_value'))['arrow_value__sum'])
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
