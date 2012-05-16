from itertools import groupby
import json
import math

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import View, ListView

from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Table

from entries.models import Competition, SessionRound, SCORING_TOTALS, SCORING_DOZENS, SCORING_FULL
from entries.views import TargetList, HeadedPdfView, BetterTargetList

from scores.forms import get_arrow_formset, get_dozen_formset
from scores.models import Score, Arrow, Dozen

from scoring.utils import class_view_decorator


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

        allocations = self.allocations

        for session in context['target_list']:
            if cache.get('bosses_cache_%d' % session.pk):
                allocations = allocations.exclude(session_entry__session_round__session=session)

        arrows = Arrow.objects.filter(score__target__in=allocations).select_related('score__target', 'score__target__session_entry__session_round__session')
        dozens = Dozen.objects.filter(score__target__in=allocations).select_related('score__target', 'score__target__session_entry__session_round__session')
        target_lookup = {}
        for arrow in arrows:
            target = arrow.score.target
            session = target.session_entry.session_round.session
            if target not in target_lookup:
                target_lookup[target] = {}
            dozen = math.floor((arrow.arrow_of_round - 1) / session.arrows_entered_per_end)
            dozen = int(dozen)
            if dozen not in target_lookup[target]:
                target_lookup[target][dozen] = []
            target_lookup[target][dozen].append(arrow)

        for session, options in context['target_list'].items():
            session_round = options['rounds'][0]
            cache_key = 'bosses_cache_%d' % session.pk
            targets = options['targets']
            bosses = options['bosses'] = cache.get(cache_key) or []
            dozens = options['dozens'] = range(1, 1 + session_round.shot_round.arrows / session_round.session.arrows_entered_per_end)
            if bosses:
                continue
            for boss, allocations in groupby(targets, lambda t: t.boss):
                combined_lookup = {}
                allocations = list(allocations)
                for dozen in dozens:
                    combined_lookup[dozen] = True
                    for allocation in allocations:
                        if (allocation not in target_lookup
                                or dozen not in target_lookup[allocation]
                                or not len(target_lookup[allocation][dozen]) == session_round.session.arrows_entered_per_end):
                            combined_lookup[dozen] = False
                bosses.append((boss, combined_lookup))
            combine = lambda x, y: x and y
            session_complete = bosses and reduce(combine, [reduce(combine, b[1].values()) for b in bosses])
            if session_complete:
                cache.set(cache_key, bosses, 30000)

        if 'ft' in self.request.GET and 'fd' in self.request.GET and 'fs' in self.request.GET:
            context['focus'] = self.request.GET['fd'] + '-' + self.request.GET['ft'] + '-' + self.request.GET['fs']

        return context


class InputScoresMobile(InputScores):
    template_name = 'scores/input_scores_mobile.html'


class InputArrowsView(View):
    template = 'input_arrows.html'
    next_url_name = 'input_scores'

    def get(self, request, slug, session_id, boss, dozen):
        competition = get_object_or_404(Competition, slug=slug)
        scores = Score.objects.filter(target__session_entry__session_round__session=session_id, target__boss=boss, target__session_entry__present=True, retired=False).order_by('target__target').select_related()
        try:
            forms = get_arrow_formset(scores, session_id, boss, dozen, scores[0].target.session_entry.session_round.session.arrows_entered_per_end)
        except IndexError:
            pass
        return render(request, self.template, locals())

    def post(self, request, slug, session_id, boss, dozen):
        competition = get_object_or_404(Competition, slug=slug)
        scores = Score.objects.filter(target__session_entry__session_round__session=session_id, target__boss=boss).order_by('target__target').select_related()
        forms = get_arrow_formset(scores, session_id, boss, dozen, scores[0].target.session_entry.session_round.session.arrows_entered_per_end, data=request.POST)
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
            return HttpResponseRedirect(reverse(self.next_url_name, kwargs={'slug': slug}) + '?fd={0}&ft={1}&fs={2}'.format(dozen, boss, session_id))
        return render(request, self.template, locals())

input_arrows = login_required(InputArrowsView.as_view())

class InputArrowsViewMobile(InputArrowsView):
    template = 'input_arrows_mobile.html'
    next_url_name = 'input_scores_mobile'

input_arrows_mobile = login_required(InputArrowsViewMobile.as_view())


class InputDozens(View):
    template = 'input_dozens.html'
    next_url_name = 'input_scores'

    def get(self, request, slug, session_id, boss, dozen):
        competition = get_object_or_404(Competition, slug=slug)
        scores = Score.objects.filter(target__session_entry__session_round__session=session_id, target__boss=boss, target__session_entry__present=True, retired=False).order_by('target__target').select_related()
        num_dozens = SessionRound.objects.filter(session__pk=session_id)[0].shot_round.arrows / 12
        try:
            forms = get_dozen_formset(scores, num_dozens, boss, dozen, scores[0].target.session_entry.session_round.session.arrows_entered_per_end)
        except IndexError:
            pass
        return render(request, self.template, locals())

    def post(self, request, slug, session_id, boss, dozen):
        competition = get_object_or_404(Competition, slug=slug)
        scores = Score.objects.filter(target__session_entry__session_round__session=session_id, target__boss=boss, target__session_entry__present=True, retired=False).order_by('target__target').select_related()
        num_dozens = SessionRound.objects.filter(session__pk=session_id)[0].shot_round.arrows / 12
        forms = get_dozen_formset(scores, num_dozens, boss, dozen, scores[0].target.session_entry.session_round.session.arrows_entered_per_end, data=request.POST)
        dozens = []
        failed = False
        for score in forms:
            if score['form'].is_valid():
                dozens.append(score['form'].save(commit=False))
                if score['score_form']:
                    if score['score_form'].is_valid():
                        score['score_form'].save(commit=False)
                    else:
                        failed = True
            else:
                failed = True
        if not failed:
            for dbdozen in dozens:
                dbdozen.save()
            for score in scores:
                score.update_score()
                score.save(force_update=True)
            return HttpResponseRedirect(reverse(self.next_url_name, kwargs={'slug': slug}) + '?fd={0}&ft={1}&fs={2}'.format(dozen, boss, session_id))
        return render(request, self.template, locals())



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

        context['results'] = self.get_categorised_results(scores)
        return context

    def get_categorised_results(self, scores):
        results = []
        for category, scores in groupby(scores, lambda s: s.target.session_entry.competition_entry.category()):
            results.append((category, list(scores)))
        return results


@class_view_decorator(login_required)
class LeaderboardCombinedNovice(LeaderboardCombined):
    title = 'Leaderboard (Novice)'

    def get_queryset(self):
        scores = super(LeaderboardCombinedNovice, self).get_queryset()
        scores = scores.filter(target__session_entry__competition_entry__novice='N')
        return scores


@class_view_decorator(login_required)
class LeaderboardCombinedExperienced(LeaderboardCombined):
    title = 'Leaderboard (Experienced)'

    def get_queryset(self):
        scores = super(LeaderboardCombinedExperienced, self).get_queryset()
        scores = scores.filter(target__session_entry__competition_entry__novice='E')
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

    def get_club_results(self, scores, max_per_team=4):
        club_results = {}
        for score in scores:
            club = score.target.session_entry.competition_entry.club
            if club not in club_results:
                club_results[club] = []
            club_results[club].append(score)
        for club, scores in club_results.iteritems():
            team = sorted(scores, key=lambda s: (s.score, s.hits, s.golds), reverse=True)[:max_per_team]
            total = sum([s.score for s in team])
            total_golds = sum([s.golds for s in team])
            club_results[club] = {'team': team, 'total': total, 'total_golds': total_golds, 'club': club}
        club_results = sorted(club_results.values(), key=lambda s: (s['total'], s['total_golds']), reverse=True)
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
        context['novice_results'] = self.get_club_results(novice_scores, 3)

        context['title'] = self.title

        return context


class LeaderboardBUTC(LeaderboardTeams):
    template_name = 'scores/leaderboard_butc.html'
    backbone_template = 'scores/leaderboard_butc_backbone.html'
    title = 'BUTC 2012'

    def render_to_response(self, context):
        if self.request.is_ajax():
            return HttpResponse(context['serialized_results'])
        return super(LeaderboardBUTC, self).render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(LeaderboardBUTC, self).get_context_data(**kwargs)
        context['serialized_results'] = json.dumps([{
            'position': i + 1,
            'id': d['club'].pk,
            'club': d['club'].short_name.replace(' Uni', ''),
            'team': [{
                'name': a.target.session_entry.competition_entry.archer.name.split(' ')[-1],
                'score': a.score,
                } for a in d['team']],
            'total': d['total'],
        } for i, d in enumerate(context['club_results'][:32])])
        context['template'] = render_to_string(self.backbone_template)
        return context


class LeaderboardSummary(LeaderboardCombined, LeaderboardTeams):
    template_name = 'scores/leaderboard_summary.html'
    title = 'Leaderboard (Summary)'

    def get_context_data(self, **kwargs):
        context = super(LeaderboardSummary, self).get_context_data(**kwargs)
        scores = context['object_list']
        exp_results = self.get_categorised_results(scores.filter(target__session_entry__competition_entry__novice='E'))
        nov_results = self.get_categorised_results(scores.filter(target__session_entry__competition_entry__novice='N'))
        scores = scores.exclude(target__session_entry__competition_entry__bowstyle__name='Compound')
        context['exp_results'] = exp_results
        context['nov_results'] = nov_results
        context['club_results'] = self.get_club_results(scores)[:10]
        novice_scores = scores.filter(target__session_entry__competition_entry__novice='N')
        context['novice_results'] = self.get_club_results(novice_scores, 3)[:10]
        for results in [exp_results, nov_results]:
            for i, info in enumerate(results):
                category, scores = info
                results[i] = (category, scores[:8])
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

    def setMargins(self, doc):
        doc.topMargin = 1.5*inch
        doc.bottomMargin = 0.7*inch

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
        num_subrounds = subrounds.count()
        if num_subrounds > 1:
            if entry.disqualified or entry.target.session_entry.session_round.session.scoring_system == SCORING_TOTALS:
                row += [None] * num_subrounds
            else:
                subround_scores = []

                if entry.target.session_entry.session_round.session.scoring_system == SCORING_FULL:
                    # Arrow of round has been stored off by a dozen
                    counter = 13
                    for subround in subrounds.order_by('-distance'):
                        subround_scores.append(entry.arrow_set.filter(arrow_of_round__in=range(counter, counter + subround.arrows)).aggregate(models.Sum('arrow_value'))['arrow_value__sum'])
                        counter += subround.arrows

                elif entry.target.session_entry.session_round.session.scoring_system == SCORING_DOZENS:
                    counter = 1
                    for subround in subrounds.order_by('-distance'):
                        subround_scores.append(entry.dozen_set.filter(dozen__in=range(counter, counter + subround.arrows / 12)).aggregate(models.Sum('total'))['total__sum'])
                        counter += subround.arrows / 12

                row += subround_scores

        scores = [
            entry.score,
            entry.golds,
            entry.xs,
        ]
        if entry.disqualified:
            scores = ['DSQ', None, None]
            row[0] = None
        elif entry.retired:
            scores = [entry.score, 'Retired', None]
        row += scores
        return row

    def get_elements(self):
        elements = []

        session_rounds, scores, sessions = self.get_results()
        for session, session_round, results in scores:
            elements.append(self.Para(session_round.shot_round, 'h1'))

            for category, entries in results:
                elements.append(self.Para(category , 'h2'))
                table_data = [self.row_from_entry(entries, entry) for entry in entries]
                if table_data:
                    gender = entries[0].target.session_entry.competition_entry.archer.gender
                    bowstyle = entries[0].target.session_entry.competition_entry.bowstyle
                    did_not_starts = session_round.sessionentry_set.select_related().filter(
                            competition_entry__archer__gender=gender,
                            competition_entry__bowstyle=bowstyle,
                    ).filter(
                            Q(targetallocation__score=None) | Q(targetallocation__score__score=0) | Q(targetallocation=None)
                    )
                    for dns in did_not_starts:
                        table_data.append([None, dns.competition_entry.archer.name, dns.competition_entry.club.name, 'DNS'])
                else:
                    #FIXME! DNS for a category where everyone shot...
                    pass
                table = Table(table_data)
                elements.append(table)
            
            elements.append(PageBreak())

        return elements

results_pdf = login_required(ResultsPdf.as_view())
