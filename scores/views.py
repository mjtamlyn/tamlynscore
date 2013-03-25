from itertools import groupby
import json
import math

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import View, ListView

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph
from reportlab.rl_config import defaultPageSize

from entries.models import Competition, SessionRound, SCORING_TOTALS, SCORING_DOZENS, SCORING_FULL
from entries.views import HeadedPdfView, TargetList

from .forms import get_arrow_formset, get_dozen_formset
from .models import Score, Arrow, Dozen
from .result_modes import get_mode

from scoring.utils import class_view_decorator


@class_view_decorator(login_required)
class InputScores(TargetList):
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


@class_view_decorator(login_required)
class LeaderboardView(View):
    template = 'leaderboard.html'
    title = 'Leaderboard'

    def get_session_rounds(self):
        return SessionRound.objects.filter(session__competition=self.competition).order_by('session__start')

    def get_results(self, qs=None):
        session_rounds = self.get_session_rounds()
        scores = [
            (
                session_round.session,
                session_round,
                Score.objects.results(session_round, qs=qs),
            )
            for session_round in session_rounds
        ]
        sessions = []
        for key, values in groupby(scores, lambda x: x[0]):
            sessions.append((key, [value[1] for value in values]))
        return session_rounds, scores, sessions

    def get_context(self, request, slug, **kwargs):
        competition = self.competition = get_object_or_404(Competition, slug=slug)
        session_rounds, scores, sessions = self.get_results()
        title = self.title
        return locals()

    def get(self, request, *args, **kwargs):
        context = self.get_context(request, *args, **kwargs)
        return render(request, self.template, context)


@class_view_decorator(login_required)
class LeaderboardCombined(ListView):
    template_name = 'scores/leaderboard_combined.html'
    title = 'Leaderboard (all archers)'

    def get_queryset(self):
        scores = Score.objects.filter(target__session_entry__competition_entry__competition__slug=self.kwargs['slug']).select_related().order_by(
                'target__session_entry__competition_entry__bowstyle',
                'target__session_entry__competition_entry__archer__gender',
                'target__session_entry__competition_entry__archer__age',
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
            total_hits = sum([s.hits for s in team])
            total_xs = sum([s.xs for s in team])
            club_results[club] = {
                'team': team,
                'total': total,
                'total_golds': total_golds,
                'total_xs': total_xs,
                'total_hits': total_hits,
                'club': club,
            }
        club_results = sorted(club_results.values(), key=lambda s: (s['total'], s['total_golds']), reverse=True)
        club_results = filter(lambda t: len(t['team']) == max_per_team, club_results)
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

        exp_scores = scores
        if not competition.novices_in_experienced_teams:
            exp_scores = exp_scores.filter(target__session_entry__competition_entry__novice='E')
        context['club_results'] = self.get_club_results(exp_scores)
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


class LeaderboardBigScreenSession(LeaderboardView):
    template = 'leaderboard_big_screen.html'

    def get_session_rounds(self):
        return SessionRound.objects.filter(session=self.kwargs['session_id'], session__competition__slug=self.kwargs['slug'])


class LeaderboardBigScreenSessionExperienced(LeaderboardBigScreenSession):
    template = 'leaderboard_big_screen.html'

    def get_results(self, qs=None):
        qs = Score.objects.filter(target__session_entry__competition_entry__novice='E')
        return super(LeaderboardBigScreenSessionExperienced, self).get_results(qs)


class LeaderboardBigScreenSessionNovice(LeaderboardBigScreenSession):
    template = 'leaderboard_big_screen.html'

    def get_results(self, qs=None):
        qs = Score.objects.filter(target__session_entry__competition_entry__novice='N')
        return super(LeaderboardBigScreenSessionNovice, self).get_results(qs)


class ResultsView(LeaderboardView):
    title = 'Results'

results = login_required(ResultsView.as_view())

class ResultsPdf(HeadedPdfView, LeaderboardSummary):
    title = 'Results'
    include_dns = True

    def setMargins(self, doc):
        doc.topMargin = 1.2*inch
        doc.bottomMargin = 0.7*inch

    def update_style(self):
        self.styles['h1'].alignment = 1
        self.styles['h2'].alignment = 1

    def get_results(self, qs=None):
        session_rounds = SessionRound.objects.filter(session__competition=self.competition).order_by('session__start')
        return [[session_rounds[0].session, session_rounds[0], Score.objects.results(qs=qs)]]
        scores = [
            (
                session_round.session,
                session_round,
                Score.objects.results(session_round, qs=qs),
            )
            for session_round in session_rounds
        ]
        sessions = []
        for key, values in groupby(scores, lambda x: x[0]):
            sessions.append((key, [value[1] for value in values]))
        return scores


    def row_from_entry(self, entries, entry, subrounds, round_scoring_type):
        row = []
        guest = entry.target.session_entry.competition_entry.guest
        if entry.disqualified or guest:
            row.append(None)
        else:
            placing = entries.index(entry) + 1
            # this is a little naive and will only work if two archers are tied, not any more.
            if placing > 1:
                previous = entries[placing - 2]
                if previous.score == entry.score and previous.golds == entry.golds and previous.hits == entry.hits and previous.xs == entry.xs:
                    placing -= 1
            row.append(placing)
        row.append(entry.target.session_entry.competition_entry.archer.name)
        row.append(entry.target.session_entry.competition_entry.club.name + (' (Guest)' if guest else ''))
        if len(subrounds) > 1 and not entries[0].target.session_entry.session_round.session.scoring_system == SCORING_TOTALS:
            if entry.disqualified or entry.target.session_entry.session_round.session.scoring_system == SCORING_TOTALS:
                row += [None] * len(subrounds)
            else:
                subround_scores = []

                if entry.target.session_entry.session_round.session.scoring_system == SCORING_FULL:
                    # Arrow of round has been stored off by a dozen
                    counter = 13
                    for subround in subrounds:
                        subround_scores.append(entry.arrow_set.filter(arrow_of_round__in=range(counter, counter + subround.arrows)).aggregate(models.Sum('arrow_value'))['arrow_value__sum'])
                        counter += subround.arrows

                elif entry.target.session_entry.session_round.session.scoring_system == SCORING_DOZENS:
                    counter = 1
                    for subround in subrounds:
                        subround_scores.append(entry.dozen_set.filter(dozen__in=range(counter, counter + subround.arrows / 12)).aggregate(models.Sum('total'))['total__sum'])
                        counter += subround.arrows / 12

                row += subround_scores

        scores = [
            entry.score,
            entry.golds,
            entry.xs,
        ] if round_scoring_type == 'X' else [
            entry.score,
            entry.hits,
            entry.golds,
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

        scores = self.get_queryset().exclude(score=0)
        nov_scores = scores.filter(target__session_entry__competition_entry__novice='N')

        if nov_scores:
            exp_scores = scores
            elements.append(self.Para('Experienced Results', 'h1'))
        else:
            exp_scores = scores
        elements += self.get_elements_for_results_set(exp_scores)
        if nov_scores:
            elements.append(self.Para('Novice Results', 'h1'))
            elements += self.get_elements_for_results_set(nov_scores)

        # Teams - FIXME assume not needed if there aren't novices (hacky way of getting student shoots)
        if nov_scores:
            round_scoring_type = nov_scores[0].target.session_entry.session_round.shot_round.scoring_type
            scores = scores.exclude(target__session_entry__competition_entry__bowstyle__name='Compound').exclude(retired=True)
            exp_scores = scores.filter(target__session_entry__competition_entry__novice='E')
            nov_scores = scores.filter(target__session_entry__competition_entry__novice='N')
            club_results = self.get_club_results(exp_scores)
            elements.append(self.Para('Experienced Teams', 'h1'))
            elements += self.get_elements_for_teams(club_results, round_scoring_type=round_scoring_type)
            nov_club_results = self.get_club_results(nov_scores, 3)
            elements.append(self.Para('Novice Teams', 'h1'))
            elements += self.get_elements_for_teams(nov_club_results, round_scoring_type=round_scoring_type)

        return elements


    def get_elements_for_results_set(self, scores):
        elements = []

        for session, session_round, results in self.get_results(qs=scores):
            if not results:
                continue
            elements.append(self.Para(session_round.shot_round, 'h1'))

            for category, entries in results:
                if not entries:
                    continue
                elements.append(self.Para(category , 'h2'))
                table_header = ['Pl.', 'Archer', 'Club']
                subrounds = session_round.shot_round.subrounds.order_by('-distance')
                if len(subrounds) > 1 and not session_round.session.scoring_system == SCORING_TOTALS:
                    table_header += ['{0}{1}'.format(subround.distance, subround.unit) for subround in subrounds]
                round_scoring_type = session_round.shot_round.scoring_type
                table_header += ['Score', '10s', 'Xs'] if round_scoring_type == 'X' else ['Score', 'Hits', 'Golds']
                table_data = [table_header]
                table_data += filter(None, [self.row_from_entry(entries, entry, subrounds, round_scoring_type) for entry in entries])
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
                        if self.include_dns:
                            table_data.append([None, dns.competition_entry.archer.name, dns.competition_entry.club.name, 'DNS'])
                else:
                    #FIXME! DNS for a category where everyone shot...
                    pass
                table = Table(table_data)
                table.setStyle(self.table_style)
                elements.append(table)

            elements.append(Spacer(self.PAGE_WIDTH, 0.25*inch))

        return elements

    def get_elements_for_teams(self, results, round_scoring_type):
        elements = []

        table_data = []
        for i, team in enumerate(results):
            table_data += [[i+1, team['club'].name] + ([
                team['total'],
                team['total_golds'],
                team['total_xs'],
            ] if round_scoring_type == 'X' else [
                team['total'],
                team['total_hits'],
                team['total_golds'],
            ])]
            table_data += [[
                None,
                score.target.session_entry.competition_entry.archer.name,
            ] + ([
                score.score,
                score.golds,
                score.xs,
            ] if round_scoring_type == 'X' else [
                score.score,
                score.hits,
                score.golds,
            ]) for score in team['team']]
        elements.append(Table(table_data))

        return elements


    table_style = TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
    ])

results_pdf = login_required(ResultsPdf.as_view())


class ResultsPdfWinners(ResultsPdf):
    include_dns = False

    def row_from_entry(self, entries, entry, subrounds, round_scoring_type):
        if entries.index(entry) >= 5:
            return None
        guest = entry.target.session_entry.competition_entry.guest
        if entry.disqualified or guest:
            return None
        return super(ResultsPdfWinners, self).row_from_entry(entries, entry, subrounds, round_scoring_type)

results_pdf_winners = login_required(ResultsPdfWinners.as_view())


class ResultsPdfOverall(ResultsPdf):
    """This view is a big hack for the AGBNS weekend."""
    title = 'Results'

    def get_elements(self):
        elements = []

        i = 1
        import csv
        session_rounds, scores, sessions = self.get_results()
        for session, session_round, results in scores[:2]:
            for category, entries in results:
                if not entries or len(entries) < 2:
                    continue
                elements.append(self.Para(category , 'h2'))
                with open('%s.csv' % i) as f:
                    data = csv.reader(f)
                    table_data = list(data)
                table = Table(table_data)
                table.setStyle(self.table_style)
                elements.append(table)
                i += 1

        return elements


results_pdf_overall = login_required(ResultsPdfOverall.as_view())




class NewLeaderboard(ListView):
    """General leaderboard/rsults generation.
    
    Strategy:
     - get the competition
     - check the mode and the format are valid
     - get the queryset of scores
     - arrange and aggregate using the ResultMode object
     - render
    """
    leaderboard = True
    title = 'Leaderboard'
    url_name = 'new_leaderboard'

    def get(self, request, *args, **kwargs):
        self.competition = self.get_competition()
        self.mode = self.get_mode()
        self.format = self.get_format()
        self.object_list = self.get_queryset()
        context = self.get_context_data(competition=self.competition, object_list=self.object_list)
        return self.render_to_response(context)

    def get_competition(self):
        competition = get_object_or_404(Competition, slug=self.kwargs['slug'])
        return competition

    def get_mode(self):
        mode = get_mode(self.kwargs['mode'])
        if not mode:
            raise Http404('No such mode')
        if not self.mode_exists(mode):
            raise Http404('No such mode for this competition')
        return mode

    def mode_exists(self, mode):
        return self.competition.result_modes.filter(mode=mode.slug).exists()

    def get_format(self):
        format = self.kwargs['format']
        if format not in ['html', 'pdf']:
            raise Http404('No such format')
        return format

    def get_queryset(self):
        # TODO: stop using blank select_related
        scores = Score.objects.filter(
            target__session_entry__competition_entry__competition=self.competition
        ).select_related().order_by(
            '-target__session_entry__competition_entry__archer__age',
            'target__session_entry__competition_entry__bowstyle',
            'target__session_entry__competition_entry__archer__gender',
            'disqualified',
            '-score', 
            '-golds', 
            '-xs'
        )
        return scores

    def get_context_data(self, **kwargs):
        kwargs['results'] = self.mode.get_results(self.competition, kwargs['object_list'], leaderboard=self.leaderboard)
        kwargs['mode'] = self.mode
        kwargs['url_name'] = self.url_name
        kwargs['title'] = self.title
        return super(NewLeaderboard, self).get_context_data(**kwargs)

    def render_to_response(self, context, **response_kwargs):
        if self.format == 'pdf':
            return self.render_to_pdf(context)
        return super(NewLeaderboard, self).render_to_response(context, **response_kwargs)

    def get_template_names(self, **kwargs):
        return ['scores/leaderboard.html']

    def render_to_pdf(self, context):
        response = HttpResponse(mimetype='application/pdf')
        self.page_width, self.page_height = defaultPageSize
        doc = SimpleDocTemplate(response, pagesize=defaultPageSize)
        self.styles = getSampleStyleSheet()
        self.styles['h1'].alignment = 1
        self.styles['h2'].alignment = 1
        elements = self.get_elements(context['results'])
        doc.build(elements, onFirstPage=self.draw_title, onLaterPages=self.draw_title)
        return response

    def draw_title(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 18)
        canvas.drawCentredString(self.page_width/2.0, self.page_height-70, u'{0}: {1}'.format(self.competition, self.title))
        canvas.restoreState()

    def get_elements(self, results):
        elements = []

        table_style = TableStyle([
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
        ])

        for section, categories in results.items():
            elements.append(Paragraph(unicode(section), self.styles['h1']))

            for category, scores in categories.items():
                elements.append(Paragraph(unicode(category), self.styles['h2']))
                table_data = [section.headers]
                for score in scores:
                    table_data += self.rows_from_score(scores, score, section)
                table = Table(table_data)
                table.setStyle(table_style)
                elements.append(table)

            return elements

    def rows_from_score(self, scores, score, section):
        row = []
        rows = [row]

        placing = scores.index(score) + 1

        # Placing
        if score.disqualified or score.guest:
            row.append(None)
        else:
            # TODO: Fix, and move all position faff to the resultmode objects
            # this is a very naive and will only work if two archers are tied, not any more.
            #if placing > 1 and not score['score'] == 'DNS':
            #    previous = scores[placing - 2]
            #    if previous.score == score['score'] and previous.golds == score['golds'] and previous['hits'] == score['hits'] and previous.xs == score['xs']:
            #        placing -= 1
            row.append(placing)

        if score.is_team:
            row += [score.club]
            for member in score.team:
                rows.append([
                    None,
                    member.target.session_entry.competition_entry.archer.name,
                ] + self.score_details(member, section))
        else:
            row += [
                score.target.session_entry.competition_entry.archer.name,
                score.target.session_entry.competition_entry.club.name + (' (Guest)' if score.guest else ''),
                'Novice' if score.target.session_entry.competition_entry.novice == 'N' else None,
            ]
        row += self.score_details(score, section)
        return rows

    def score_details(self, score, section):
        if score.disqualified:
            scores = ['DSQ', None, None]
        elif score.retired:
            scores = [score.score, 'Retired', None]
        elif section.round.scoring_type == 'X':
            scores = [
                score.score,
                score.hits,
                score.xs,
            ]
        else:
            scores = [
                score.score,
                score.hits,
                score.golds,
            ]
        return scores


class NewResults(NewLeaderboard):
    leaderboard = False
    title = 'Results'
    url_name = 'new_results'

    def mode_exists(self, mode):
        return self.competition.result_modes.filter(mode=mode.slug, leaderboard_only=False).exists()
