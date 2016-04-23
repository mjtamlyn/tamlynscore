import copy
import csv
from itertools import groupby
import functools
import math

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic import View, ListView, TemplateView

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph
from reportlab.rl_config import defaultPageSize

from core.models import County
from entries.models import Competition, SessionRound, CompetitionEntry, ResultsMode
from entries.views import TargetList, CompetitionMixin
from olympic.models import OlympicRound, Result

from .forms import get_arrow_formset, get_dozen_formset
from .models import Score, Arrow, Dozen
from .result_modes import get_mode


class InputScores(TargetList):
    template_name = 'scores/input_scores.html'
    admin_required = True

    def get_queryset(self):
        return super(InputScores, self).get_queryset().order_by('session_entry__session_round__session', 'boss', 'target').select_related('score')

    def add_unallocated_entries(self, target_list):
        pass

    def get_context_data(self, **kwargs):
        context = super(InputScores, self).get_context_data(**kwargs)

        for allocation in self.allocations.filter(score__isnull=True):
            Score.objects.create(target=allocation)

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


class InputScoresTeam(CompetitionMixin, TemplateView):
    template_name = 'scores/input_scores_team.html'

    def get_context_data(self, **kwargs):
        context = super(InputScoresTeam, self).get_context_data(**kwargs)
        entries = CompetitionEntry.objects.filter(competition=self.competition).select_related('county').filter(county__isnull=False)
        teams = set(entry.county for entry in entries)
        context['teams'] = sorted(teams, key=lambda t: str(t))
        context['dozens'] = range(1, 13)
        return context


class InputScoresMobile(InputScores):
    template_name = 'scores/input_scores_mobile.html'


class InputArrowsView(CompetitionMixin, TemplateView):
    template_name = 'input_arrows.html'
    next_url_name = 'input_scores'

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
            return HttpResponseRedirect(reverse(self.next_url_name, kwargs={'slug': slug}) + '?fd={0}&ft={1}&fs={2}'.format(dozen, boss, session_id))
        return render(request, self.template, locals())


class InputArrowsViewMobile(InputArrowsView):
    template = 'input_arrows_mobile.html'
    next_url_name = 'input_scores_mobile'


class InputArrowsArcher(TemplateView):
    template_name = 'scores/input_arrows_archer.html'

    def get_context_data(self, **kwargs):
        competition = get_object_or_404(Competition, slug=self.kwargs['slug'])
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
        return {
            'competition': competition,
            'entry': entry,
            'layout': layout,
            'score': score,
            'round': round,
        }


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

    def render_to_pdf(self, context):
        response = HttpResponse(content_type='application/pdf')
        self.page_width, self.page_height = defaultPageSize
        doc = SimpleDocTemplate(response, pagesize=defaultPageSize)
        self.styles = getSampleStyleSheet()
        self.styles['h1'].alignment = 1
        self.styles['h2'].alignment = 1
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
                elements.append(Paragraph(str(category), self.styles['h2']))
                table_data = [section.headers]
                for score in scores:
                    table_data += self.rows_from_score(scores, score, section)
                table = Table(table_data)
                table.setStyle(table_style)
                elements.append(table)

            elements.append(Spacer(0.25 * inch, 0.25 * inch))

        return elements

    def rows_from_score(self, scores, score, section):
        row = [score.placing]
        rows = [row]

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
            if self.competition.has_wa_age_groups:
                if score.target.session_entry.competition_entry.wa_age:
                    row.append(score.target.session_entry.competition_entry.get_wa_age_display())
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
                        if self.competition.has_wa_age_groups:
                            if score.target.session_entry.competition_entry.wa_age:
                                row.append(score.target.session_entry.competition_entry.get_wa_age_display())
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


class Leaderboard(CompetitionMixin, PDFResultsRenderer, CSVResultsRenderer, JSONResultsRenderer, ListView):
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

    def get_context_data(self, **kwargs):
        kwargs['results'] = self.mode.get_results(self.competition, kwargs['object_list'], leaderboard=self.leaderboard, request=self.request)
        kwargs['mode'] = self.mode
        kwargs['url_name'] = self.url_name
        kwargs['title'] = self.title
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


class RankingsExport(CompetitionMixin, View):
    def get(self, request, *args, **kwargs):
        entries = self.get_entries()
        rounds = self.get_rounds()
        olympic_rounds = self.get_olympic_rounds()
        scores = self.get_scores()
        headings = self.get_headings(rounds, olympic_rounds)
        data = self.match_details(entries, rounds, olympic_rounds, scores)
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(headings)
        writer.writerows(data)
        return response

    def get_entries(self):
        return CompetitionEntry.objects.filter(competition=self.competition).select_related('archer', 'club', 'bowstyle')

    def get_rounds(self):
        return SessionRound.objects.filter(session__competition=self.competition).select_related('shot_round')

    def get_olympic_rounds(self):
        return OlympicRound.objects.filter(olympicsessionround__session__competition=self.competition).distinct()

    def get_scores(self):
        return Score.objects.filter(
            target__session_entry__competition_entry__competition=self.competition
        ).select_related(
            'target__session_entry',
        )

    def get_headings(self, rounds, olympic_rounds):
        headings = ['Name', 'Club', 'Gender', 'Bowstyle', 'AGB number']
        for r in rounds:
            name = r.shot_round.name
            headings += [
                '%s - Score' % name,
                '%s - 10s' % name,
                '%s - Xs' % name,
                '%s - Retired/DNS' % name,
            ]
        for r in olympic_rounds:
            headings.append(r)
        return headings

    def match_details(self, entries, rounds, olympic_rounds, scores):
        data = {}
        round_indices = {}
        for entry in entries:
            data[entry.pk] = [
                entry.archer.name,
                entry.team_name(),
                entry.archer.get_gender_display(),
                entry.bowstyle,
                entry.archer.agb_number,
            ] + [''] * (len(rounds) * 4 + len(olympic_rounds))
        for i, r in enumerate(rounds):
            round_indices[r.pk] = 5 + 4 * i
        for score in scores:
            entry = score.target.session_entry.competition_entry_id
            index = round_indices[score.target.session_entry.session_round_id]
            if score.score == 0:
                data[entry][index + 3] = 'DNS'
            else:
                data[entry][index] = score.score
                data[entry][index + 1] = score.golds
                data[entry][index + 2] = score.xs
                if score.retired:
                    data[entry][index + 3] = 'Retired'
        for i, r in enumerate(olympic_rounds):
            index = len(rounds) * 4 + 5 + i
            results = Result.objects.filter(
                seed__session_round__shot_round=r,
                seed__entry__competition=self.competition,
            ).order_by('total').select_related('seed__entry__bowstyle').exclude(dns=True)
            for result in results:
                entry = result.seed.entry
                if entry.bowstyle.name == 'Compound':
                    data[entry.pk][index] = result.total
                else:
                    data[entry.pk][index] = 'Match Completed'
        return data.values()


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
