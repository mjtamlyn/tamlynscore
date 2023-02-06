import copy
import csv
import functools
import math
from itertools import groupby

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Max
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import ListView, TemplateView, View

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)
from reportlab.rl_config import defaultPageSize

from core.models import County
from entries.models import (
    Competition, CompetitionEntry, ResultsMode, SessionRound,
)
from entries.views import CompetitionMixin, TargetList
from olympic.models import OlympicSessionRound

from .forms import get_arrow_formset, get_dozen_formset
from .models import Arrow, Dozen, Score
from .result_modes import ByRound, get_mode


class InputScores(TargetList):
    template_name = 'scores/input_scores.html'
    admin_required = True

    def get_queryset(self):
        return super(InputScores, self).get_queryset().order_by('session_entry__session_round__session', 'boss', 'target').select_related('score')

    def add_unallocated_entries(self, target_list):
        pass

    def get_context_data(self, **kwargs):
        context = super(InputScores, self).get_context_data(**kwargs)

        modified = False
        for allocation in self.allocations.filter(score__isnull=True):
            Score.objects.create(target=allocation)
            modified = True
        if modified:
            context['target_list'] = self.get_target_list()

        allocations = self.allocations.select_related('score')

        for session in context['target_list']:
            if cache.get('bosses_cache_%d' % session.pk):
                allocations = allocations.exclude(session_entry__session_round__session=session)

        arrows = Arrow.objects.filter(score__target__in=allocations).values('arrow_of_round', 'score__target_id', 'score__target__session_entry__session_round__session__arrows_entered_per_end')
        dozens = Dozen.objects.filter(score__target__in=allocations).values('score__target_id', 'dozen', 'score__target__session_entry__session_round__session__arrows_entered_per_end')
        target_lookup = {}
        for arrow in arrows:
            target = arrow['score__target_id']
            entered_per_end = arrow['score__target__session_entry__session_round__session__arrows_entered_per_end']
            if target not in target_lookup:
                target_lookup[target] = {}
            dozen = math.floor((arrow['arrow_of_round'] - 1) / entered_per_end)
            dozen = int(dozen)
            if dozen not in target_lookup[target]:
                target_lookup[target][dozen] = []
            target_lookup[target][dozen].append(arrow)

        for dozen in dozens:
            target = dozen['score__target_id']
            entered_per_end = dozen['score__target__session_entry__session_round__session__arrows_entered_per_end']
            if target not in target_lookup:
                target_lookup[target] = {}
            if dozen['dozen'] not in target_lookup[target]:
                target_lookup[target][dozen['dozen']] = range(entered_per_end)

        for session, options in context['target_list'].items():
            session_round = options['rounds'][0]
            cache_key = 'bosses_cache_%d' % session.pk
            targets = options['targets']
            bosses = options['bosses'] = cache.get(cache_key) or []
            dozens = options['dozens'] = range(1, 1 + int(session_round.shot_round.arrows / session_round.session.arrows_entered_per_end))
            if bosses:
                continue
            for boss, allocations in groupby(targets, lambda t: t.boss):
                combined_lookup = {}
                allocations = list(allocations)
                for dozen in dozens:
                    combined_lookup[dozen] = True
                    for allocation in allocations:
                        if allocation.session_entry.present and not allocation.score.retired and (
                            allocation.id not in target_lookup or
                            dozen not in target_lookup[allocation.id] or
                            not len(target_lookup[allocation.id][dozen]) == session_round.session.arrows_entered_per_end
                        ):
                            combined_lookup[dozen] = False
                bosses.append((boss, combined_lookup))
            session_complete = bosses and functools.reduce(
                lambda x, y: x and y,
                [functools.reduce(lambda x, y: x and y, b[1].values()) for b in bosses],
            )
            if session_complete:
                cache.set(cache_key, bosses, 30000)

        if 'ft' in self.request.GET and 'fd' in self.request.GET and 'fs' in self.request.GET:
            context['focus'] = self.request.GET['fd'] + '-' + self.request.GET['ft'] + '-' + self.request.GET['fs']

        return context


class InputScoresMobile(InputScores):
    template_name = 'scores/input_scores_mobile.html'


class InputArrowsView(CompetitionMixin, TemplateView):
    template_name = 'input_arrows.html'
    next_url_name = 'input_scores'

    def get_next_exists(self, session_id, boss):
        return Score.objects.filter(target__session_entry__session_round__session=session_id, target__boss=int(boss) + 1).order_by('target__target').exists()

    def get_context_data(self, **kwargs):
        context = super(InputArrowsView, self).get_context_data(**kwargs)
        session_id = self.kwargs['session_id']
        boss = self.kwargs['boss']
        dozen = self.kwargs['dozen']
        scores = Score.objects.filter(target__session_entry__session_round__session=session_id, target__boss=boss, target__session_entry__present=True).order_by('target__target').select_related()
        try:
            forms = get_arrow_formset(scores, session_id, boss, dozen, scores[0].target.session_entry.session_round.session.arrows_entered_per_end)
            round = scores[0].target.session_entry.session_round.shot_round
        except IndexError:
            forms = None
            round = None
        context.update({
            'scores': scores,
            'forms': forms,
            'round': round,
            'dozen': dozen,
            'boss': boss,
            'next_exists': self.get_next_exists(session_id, boss),
        })
        return context

    def post(self, request, slug, session_id, boss, dozen):
        scores = Score.objects.filter(target__session_entry__session_round__session=session_id, target__boss=boss).order_by('target__target').select_related()
        forms = get_arrow_formset(scores, session_id, boss, dozen, scores[0].target.session_entry.session_round.session.arrows_entered_per_end, data=request.POST)
        arrows = []
        failed = False
        for score in forms:
            score['retiring_form'].save()
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
            if self.request.POST.get('next'):
                success_url = reverse('input_arrows', kwargs={'slug': slug, 'session_id': session_id, 'boss': int(boss) + 1, 'dozen': dozen})
            else:
                success_url = reverse(self.next_url_name, kwargs={'slug': slug}) + '?fd={0}&ft={1}&fs={2}'.format(dozen, boss, session_id)
            return HttpResponseRedirect(success_url)
        next_exists = self.get_next_exists(session_id, boss)
        return render(request, self.template, locals())


class InputArrowsViewMobile(InputArrowsView):
    template = 'input_arrows_mobile.html'
    next_url_name = 'input_scores_mobile'


class InputArrowsArcher(CompetitionMixin, TemplateView):
    template_name = 'scores/input_arrows_archer.html'
    admin_required = False

    def get_context_data(self, **kwargs):
        score = Score.objects.get(pk=self.kwargs['score_id'])
        entry = score.target.session_entry
        round = entry.session_round.shot_round
        per_end = entry.session_round.session.arrows_entered_per_end
        layout = [{
            'scores': ['-'] * per_end,
            'doz': 0,
            'hits': 0,
            'golds': 0,
            'xs': 0,
            'et1': 0,
            'et2': 0,
            'rt': 0,
        } for i in range(int(round.arrows / per_end))]
        arrows = score.arrow_set.all()
        for arrow in arrows:
            dozen = int((arrow.arrow_of_round - 13) / per_end)
            point = arrow.arrow_of_round % per_end - 1
            layout[dozen]['scores'][point] = str(arrow)
            layout[dozen]['doz'] += arrow.arrow_value
            if point < 6 and point >= 0:
                layout[dozen]['et1'] += arrow.arrow_value
            else:
                layout[dozen]['et2'] += arrow.arrow_value
            if arrow.arrow_value:
                layout[dozen]['hits'] += 1
            if arrow.arrow_value == 10 or (arrow.arrow_value == 9 and round.scoring_type == 'F'):
                layout[dozen]['golds'] += 1
            if arrow.is_x:
                layout[dozen]['xs'] += 1
        rt = 0
        for dozen in layout:
            rt += dozen['doz']
            dozen['rt'] = rt
        context = super().get_context_data(**kwargs)
        context.update({
            'entry': entry,
            'layout': layout,
            'score': score,
            'round': round,
        })
        return context


class InputDozens(CompetitionMixin, TemplateView):
    template_name = 'input_dozens.html'
    next_url_name = 'input_scores'

    def get_next_exists(self, session_id, boss):
        return Score.objects.filter(target__session_entry__session_round__session=session_id, target__boss=int(boss) + 1).order_by('target__target').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scores = Score.objects.filter(
            target__session_entry__session_round__session=self.kwargs['session_id'],
            target__boss=self.kwargs['boss'],
            target__session_entry__present=True,
            retired=False,
        ).order_by('target__target').select_related()
        next_exists = self.get_next_exists(self.kwargs['session_id'], self.kwargs['boss'])
        num_dozens = int(SessionRound.objects.filter(session__pk=self.kwargs['session_id'])[0].shot_round.arrows / 12)
        try:
            context['forms'] = get_dozen_formset(scores, num_dozens, self.kwargs['dozen'])
        except IndexError:
            pass
        context.update({
            'next_exists': next_exists,
        })
        return context

    def post(self, request, slug, session_id, boss, dozen):
        competition = self.competition
        scores = Score.objects.filter(
            target__session_entry__session_round__session=session_id,
            target__boss=boss,
            target__session_entry__present=True,
            retired=False,
        ).order_by('target__target').select_related()
        num_dozens = SessionRound.objects.filter(session__pk=session_id)[0].shot_round.arrows / 12
        try:
            forms = get_dozen_formset(scores, num_dozens, dozen, data=request.POST)
        except IndexError:
            forms = []
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
            if self.request.POST.get('next'):
                success_url = reverse('input_dozens', kwargs={'slug': slug, 'session_id': session_id, 'boss': int(boss) + 1, 'dozen': dozen})
            else:
                success_url = reverse(self.next_url_name, kwargs={'slug': slug}) + '?fd={0}&ft={1}&fs={2}'.format(dozen, boss, session_id)
            return HttpResponseRedirect(success_url)
        next_exists = self.get_next_exists(session_id, boss)
        return render(request, self.template, locals())


class InputDozensTeam(View):
    template = 'scores/input_dozens_team.html'
    next_url_name = 'input_scores_team'

    def get(self, request, slug, team_id, dozen):
        competition = get_object_or_404(Competition, slug=slug)
        team = get_object_or_404(County, pk=team_id)
        scores = Score.objects.filter(
            target__session_entry__competition_entry__county=team,
            target__session_entry__present=True,
            retired=False,
        ).order_by('target__boss', 'target__target').select_related()
        num_dozens = 12
        try:
            forms = get_dozen_formset(scores, num_dozens, dozen=dozen)
        except IndexError:
            pass
        return render(request, self.template, locals())

    def post(self, request, slug, team_id, dozen):
        competition = get_object_or_404(Competition, slug=slug)
        team = get_object_or_404(County, pk=team_id)
        scores = Score.objects.filter(
            target__session_entry__competition_entry__county=team,
            target__session_entry__present=True,
            retired=False,
        ).order_by('target__boss', 'target__target').select_related()
        num_dozens = 12
        try:
            forms = get_dozen_formset(scores, num_dozens, dozen, data=request.POST)
        except IndexError:
            forms = []
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
            success_url = reverse(self.next_url_name, kwargs={'slug': slug})
            return HttpResponseRedirect(success_url)
        return render(request, self.template, locals())


class PDFResultsRenderer(object):
    PAGE_HEIGHT = defaultPageSize[1]
    PAGE_WIDTH = defaultPageSize[0]

    def set_styles(self):
        self.styles = getSampleStyleSheet()
        self.styles['h1'].alignment = 1
        self.styles['h2'].alignment = 1

    def render_to_pdf(self, context):
        response = HttpResponse(content_type='application/pdf')
        self.page_width, self.page_height = defaultPageSize
        doc = SimpleDocTemplate(response, pagesize=defaultPageSize)
        self.set_styles()
        elements = self.get_elements(context['results'])
        if self.competition.sponsors.exists():
            doc.bottomMargin = 1.5 * inch
        doc.build(elements, onFirstPage=self.draw_title, onLaterPages=self.draw_title)
        return response

    def draw_title(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 18)
        canvas.drawCentredString(self.page_width / 2.0, self.page_height - 70, u'{0}: {1}'.format(self.competition, self.title))
        sponsors = self.competition.sponsors.all()
        if sponsors:
            canvas.drawImage(sponsors[0].logo.path, 50, -50, width=self.PAGE_WIDTH - 100, preserveAspectRatio=True, anchor='nw')
        canvas.restoreState()

    def get_elements(self, results):
        elements = []

        table_style = TableStyle([
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 3.5),
        ])

        for section, categories in results.items():
            if not categories:
                continue
            elements.append(Paragraph(str(section), self.styles['h1']))

            for category, scores in categories.items():
                category_table_style = copy.copy(table_style)
                elements.append(Paragraph(str(category), self.styles['h2']))
                table_data = [section.headers]
                for i, score in enumerate(scores):
                    table_data += self.rows_from_score(scores, score, section, i, category_table_style)
                table = Table(table_data)
                table.setStyle(table_style)
                elements.append(table)

            elements.append(Spacer(0.25 * inch, 0.25 * inch))

        return elements

    def rows_from_score(self, scores, score, section, index, table_style):
        row = [score.placing]
        rows = [row]

        if getattr(score, 'missed_cut', None):
            table_style.add('BACKGROUND', (0, index + 1), (-1, index + 2), colors.lightgrey),

        team_style = copy.copy(self.styles['Normal'])
        team_style.fontName = 'Helvetica-Bold'
        if score.is_team:
            row += [Paragraph(str(score.club), team_style)]
            for member in score.team:
                rows.append([
                    None,
                    member.target.session_entry.competition_entry.archer.name,
                ] + self.mode.score_details(member, section))
        else:
            row += [
                score.target.session_entry.competition_entry.archer.name,
                ' '.join(filter(None, [score.target.session_entry.competition_entry.team_name(), '(Guest)' if score.guest else ''])),
            ]
            if self.competition.has_novices:
                if score.target.session_entry.competition_entry.novice == 'N':
                    row.append('Novice')
                else:
                    row.append(None)
        row += self.mode.score_details(score, section)
        return rows


class CSVResultsRenderer(object):
    def render_to_csv(self, context):
        response = HttpResponse(content_type='text/csv')
        data = []
        for section, categories in context['results'].items():
            for category, scores in categories.items():
                for score in scores:
                    row = [str(section), str(category)]
                    if getattr(score, 'team', None):
                        row += [score.club] + self.mode.score_details(score, section)
                        for member in score.team:
                            row += [
                                member.target.session_entry.competition_entry.archer.name,
                            ] + self.mode.score_details(member, section)
                    else:
                        row += [
                            score.target.session_entry.competition_entry.archer.name,
                            score.target.session_entry.competition_entry.club.name + (' (Guest)' if score.guest else ''),
                        ]
                        if self.competition.has_novices:
                            if score.target.session_entry.competition_entry.novice == 'N':
                                row.append('Novice')
                            else:
                                row.append('')
                        row += self.mode.score_details(score, section)
                    data.append(row)
        writer = csv.writer(response)
        writer.writerows(data)
        return response


class JSONResultsRenderer(object):
    def render_to_json(self, context):
        results = self.mode.serialize(context['results'])
        return HttpResponse(results, content_type='application/json')


class ResultModeMixin(object):
    def get_scores(self):
        scores = Score.objects.filter(
            target__session_entry__competition_entry__competition=self.competition
        ).select_related(
            'target',
            'target__session_entry',
            'target__session_entry__session_round',
            'target__session_entry__session_round__shot_round',
            'target__session_entry__competition_entry',
            'target__session_entry__competition_entry__competition',
            'target__session_entry__competition_entry__archer',
            'target__session_entry__competition_entry__bowstyle',
            'target__session_entry__competition_entry__club',
        ).order_by(
            '-target__session_entry__competition_entry__age',
            '-target__session_entry__competition_entry__agb_age',
            'target__session_entry__competition_entry__novice',
            'target__session_entry__competition_entry__bowstyle',
            'target__session_entry__competition_entry__archer__gender',
            'disqualified',
            '-score',
            '-golds',
            '-xs'
        )
        return scores


class Leaderboard(ResultModeMixin, CompetitionMixin, PDFResultsRenderer, CSVResultsRenderer, JSONResultsRenderer, ListView):
    """General leaderboard/results generation.

    Strategy:
     - get the competition
     - check the mode and the format are valid
     - get the queryset of scores
     - arrange and aggregate using the ResultMode object
     - render
    """
    admin_required = False
    leaderboard = True
    title = 'Leaderboard'
    url_name = 'leaderboard'
    include_distance_breakdown = False

    def get(self, request, *args, **kwargs):
        self.format = self.get_format()
        self.mode = self.get_mode()
        self.object_list = self.get_queryset()
        context = self.get_context_data(object_list=self.object_list)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.format = self.get_format()
        self.mode, obj = self.get_mode(load=True)
        self.object_list = self.get_queryset()
        context = self.get_context_data(competition=self.competition, object_list=self.object_list)
        obj.json = self.mode.serialize(context['results'])
        obj.save()
        return HttpResponseRedirect(request.get_full_path())

    def get_mode(self, load=False):
        mode = get_mode(self.kwargs['mode'], include_distance_breakdown=self.include_distance_breakdown, hide_golds=self.get_hide_golds())
        if not mode:
            raise Http404('No such mode')
        if load:
            exists, obj = self.mode_exists(mode, load=True)
        else:
            exists = self.mode_exists(mode)
        if not exists:
            raise Http404('No such mode for this competition')
        return (mode, obj) if load else mode

    def mode_exists(self, mode, load=False):
        if load:
            try:
                obj = self.competition.result_modes.filter(mode=mode.slug).get()
            except ResultsMode.DoesNotExist:
                return False, None
            else:
                return True, obj
        else:
            return self.competition.result_modes.filter(mode=mode.slug).exists()

    def get_format(self):
        format = self.kwargs['format']
        if format not in ['html', 'pdf', 'pdf-summary', 'big-screen', 'csv', 'json']:
            raise Http404('No such format')
        return format

    def get_queryset(self):
        return self.get_scores()

    def get_context_data(self, **kwargs):
        kwargs['results'] = self.mode.get_results(self.competition, kwargs['object_list'], leaderboard=self.leaderboard, request=self.request)
        kwargs['mode'] = self.mode
        kwargs['url_name'] = self.url_name
        kwargs['title'] = self.title
        kwargs['leaderboard'] = self.leaderboard
        return super(Leaderboard, self).get_context_data(**kwargs)

    def get_hide_golds(self):
        if self.format == 'big-screen':
            return True
        return False

    def render_to_response(self, context, **response_kwargs):
        results = context['results']
        if self.format == 'pdf':
            return self.render_to_pdf(context)
        elif self.format == 'pdf-summary':
            context['results'] = self.cut_results(results)
            return self.render_to_pdf(context)
        elif self.format == 'csv':
            return self.render_to_csv(context)
        elif self.format == 'json':
            return self.render_to_json(context)
        for section in results:
            for category in results[section]:
                for score in results[section][category]:
                    score.details = self.mode.score_details(score, section)
                    if getattr(score, 'team', None):
                        for archer in score.team:
                            archer.details = self.mode.score_details(archer, section)
        return super(Leaderboard, self).render_to_response(context, **response_kwargs)

    def cut_results(self, results):
        for section, categories in results.items():
            for category, scores in categories.items():
                results[section][category] = scores[:8]
        return results

    def get_template_names(self, **kwargs):
        if self.format == 'big-screen':
            return ['scores/leaderboard_big_screen.html']
        return ['scores/leaderboard.html']


class Results(Leaderboard):
    leaderboard = False
    title = 'Results'
    url_name = 'results'
    include_distance_breakdown = True

    def mode_exists(self, mode, load=False):
        if load:
            try:
                obj = self.competition.result_modes.filter(mode=mode.slug, leaderboard_only=False).get()
            except ResultsMode.DoesNotExist:
                return False, None
            else:
                return True, obj
        else:
            return self.competition.result_modes.filter(mode=mode.slug, leaderboard_only=False).exists()


class RankingsExport(ResultModeMixin, CompetitionMixin, View):
    def get(self, request, *args, **kwargs):
        entries = self.get_entries()
        scores = self.get_scores()
        headings = self.get_headings()
        archer_details = self.archer_details(entries, scores)
        by_round_results = ByRound().get_results(
            self.competition,
            scores,
            leaderboard=False,
            request=self.request,
        )
        self.annotate_round_data(by_round_results, archer_details)
        h2h_rounds = OlympicSessionRound.objects.filter(session__competition=self.competition)
        self.annotate_h2h_data(h2h_rounds, archer_details)
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(headings)
        writer.writerows(archer_details.values())
        return response

    def get_entries(self):
        return CompetitionEntry.objects.filter(competition=self.competition).select_related('archer', 'club', 'bowstyle')

    def get_scores(self):
        return Score.objects.filter(
            target__session_entry__competition_entry__competition=self.competition
        ).select_related(
            'target__session_entry',
        )

    def get_headings(self):
        headings = ['AGB Number', 'First Name', 'Last Name', 'Club', 'Bowstyle', 'Division']
        max_number_of_rounds = self.competition.competitionentry_set.annotate(session_count=Count('sessionentry')).aggregate(count=Max('session_count'))['count'] or 0
        for i in range(max_number_of_rounds):
            headings += [
                'Round %s' % (i + 1),
                'Placing',
                'Score',
                '10s',
                'Xs'
            ]
        has_h2h = OlympicSessionRound.objects.filter(session__competition=self.competition).exists()
        if has_h2h:
            headings += ['H2H Placing']
        return headings

    def get_division(self, entry):
        division = ''
        if entry.archer.gender == 'G':
            division += 'M'
        else:
            division += 'W'
        if self.competition.has_agb_age_groups:
            division = entry.agb_age + division
        return division

    def archer_details(self, entries, scores):
        data = {}
        for entry in entries:
            data[entry.pk] = [
                entry.archer.agb_number,
                ' '.join(entry.archer.name.split(' ')[:-1]),
                entry.archer.name.split(' ')[-1],
                entry.team_name(),
                entry.bowstyle.name[0],
                self.get_division(entry),
            ]
        return data

    def annotate_round_data(self, results, archers):
        for shot_round, categories in results.items():
            for category, results in categories.items():
                for result in results:
                    entry = result.target.session_entry.competition_entry
                    archers[entry.pk] += [
                        shot_round,
                        result.placing,
                        result.score,
                        result.golds,
                        result.xs,
                    ]
        return archers

    def annotate_h2h_data(self, h2hs, archers):
        for h2h_round in h2hs:
            results = h2h_round.get_results().results
            for seeding in results:
                archers[seeding.entry_id] += [seeding.rank]
        return archers


class PublicResultsMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.competition = Competition.objects.get(slug=settings.CURRENT_EVENT)
        self.modes = self.competition.result_modes.order_by('mode').exclude(json='')
        return super(PublicResultsMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['competition'] = self.competition
        kwargs['modes'] = self.modes
        return super(PublicResultsMixin, self).get_context_data(**kwargs)


class ResultsSummaryFromCache(PublicResultsMixin, TemplateView):
    template_name = 'scores/public_leaderboard_summary.html'

    def get_context_data(self, **kwargs):
        db_modes = self.modes
        kwargs['results'] = []
        for db_mode in db_modes:
            mode = get_mode(db_mode.mode, include_distance_breakdown=False, hide_golds=False)
            if db_mode.json:
                results = self.cut_results(mode.deserialize(db_mode.json))
                kwargs['results'].append({
                    'name': str(mode),
                    'results': results
                })
        return super(ResultsSummaryFromCache, self).get_context_data(**kwargs)

    def cut_results(self, results):
        for section, categories in results.items():
            for category, scores in categories.items():
                results[section][category] = scores[:8]
        return results


class ResultsFromCache(PublicResultsMixin, TemplateView):
    template_name = 'scores/public_leaderboard.html'

    def get_context_data(self, **kwargs):
        db_mode = self.competition.result_modes.get(mode=self.kwargs['mode'])
        mode = get_mode(db_mode.mode, include_distance_breakdown=False, hide_golds=False)
        if db_mode.json:
            kwargs['results'] = mode.deserialize(db_mode.json)
        else:
            kwargs['results'] = {}
        return super(ResultsFromCache, self).get_context_data(**kwargs)
