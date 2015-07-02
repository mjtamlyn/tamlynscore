from collections import OrderedDict

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Prefetch
from django.http import HttpResponseRedirect
from django.views.generic import View, TemplateView, FormView
from django.shortcuts import render, get_object_or_404

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import KeepTogether, PageBreak, Spacer, Table, TableStyle
from reportlab.rl_config import defaultPageSize

from entries.models import Competition
from entries.views import CompetitionMixin, ScoreSheetsPdf, HeadedPdfView
from scores.models import Score
from scores.result_modes import BaseResultMode
from scores.views import PDFResultsRenderer
from scoring.utils import class_view_decorator
from olympic.models import OlympicSessionRound, Seeding, Match, Result
from olympic.forms import ResultForm, SetupForm

from itertools import groupby


@class_view_decorator(login_required)
class OlympicIndex(View):
    def get(self, request, slug):
        competition = get_object_or_404(Competition, slug=slug)
        session_rounds = OlympicSessionRound.objects.filter(session__competition=competition).order_by('session__start').select_related()
        session_info = [(
            session_round.session,
            session_round,
            session_round.seeding_set.all().select_related().order_by('seed').prefetch_related('result_set'),
            Score.objects.results(session_round.ranking_round, category=session_round.category),
        ) for session_round in session_rounds]
        sessions = []
        for key, values in groupby(session_info, lambda x: x[0]):
            sessions.append((key, [value[1] for value in values]))

        if 'remove-all' in request.GET:
            Seeding.objects.filter(session_round__pk=request.GET['remove-all']).delete()
        return render(request, 'olympic_index.html', locals())

    def post(self, request, slug):
        session_round = OlympicSessionRound.objects.get(pk=request.POST['form-id'].replace('confirm-seedings-', ''))
        score_ids = map(lambda s: int(s.replace('score-', '')), filter(lambda s: s.startswith('score-'), request.POST))
        scores = Score.objects.filter(pk__in=score_ids)
        session_round.set_seedings(scores)
        return self.get(request, slug)


class FieldPlanMixin(CompetitionMixin):
    def dispatch(self, request, *args, **kwargs):
        # Use the slug because CompetitionMixin hasn't loaded the competition yet
        self.session_rounds = OlympicSessionRound.objects.filter(session__competition__slug=self.kwargs['slug'])
        return super(FieldPlanMixin, self).dispatch(request, *args, **kwargs)

    def get_matches(self):
        return Match.objects.filter(session_round__session__competition=self.competition).select_related('session_round', 'session_round__category')

    def get_field_plan(self):
        matches = self.get_matches()
        if len(matches) == 0:
            return None
        max_timing = (max(matches, key=lambda m: m.timing)).timing
        max_target = (max(matches, key=lambda m: m.target)).target  # slight assumption max target will never be target 2
        levels = ['Finals', 'Semis', 'Quarters', '1/8', '1/16', '1/32', '1/64', '1/128']
        passes = 'ABCDEFGHIJK'

        layout = [[{} for i in range(max_target + 1)] for j in range(max_timing + 1)]
        for i, row in enumerate(layout[1:]):
            row[0] = 'Pass %s' % passes[i]
        for i in range(max_target):
            layout[0][i + 1] = i + 1
        for m in matches:
            layout[m.timing][m.target] = {
                'category': m.session_round.category,
                'level': levels[m.level - 1],
            }
            if m.target_2:
                layout[m.timing][m.target_2] = {
                    'category': m.session_round.category,
                    'level': levels[m.level - 1],
                }
        for row in layout[1:]:
            current = {}
            for spot in row[1:]:
                if spot and not spot.get('category') == current.get('category'):
                    current = spot
                    current['width'] = 1
                elif spot:
                    current['width'] += 1
                elif spot is None:
                    current = {}
        return layout

    def get_context_data(self, **kwargs):
        context = super(FieldPlanMixin, self).get_context_data(**kwargs)
        context['field_plan'] = self.get_field_plan()
        return context


@class_view_decorator(login_required)
class OlympicSetup(FieldPlanMixin, FormView):
    form_class = SetupForm
    template_name = 'olympic/setup.html'

    def get_form_kwargs(self):
        kwargs = super(OlympicSetup, self).get_form_kwargs()
        kwargs['session_rounds'] = self.session_rounds
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(OlympicSetup, self).form_valid(form)

    def get_success_url(self):
        return self.request.get_full_path()


@class_view_decorator(login_required)
class OlympicSeedingsPDF(PDFResultsRenderer, View):
    def get(self, request, slug):
        self.competition = get_object_or_404(Competition, slug=slug)
        self.title = 'Seedings'
        session_rounds = OlympicSessionRound.objects.filter(session__competition=self.competition).order_by('session__start').select_related()
        results = OrderedDict()
        self.mode = result_mode = BaseResultMode()
        for session_round in session_rounds:
            shot_round = session_round.ranking_round.shot_round
            section = result_mode.get_section_for_round(shot_round)
            if session_round not in results:
                results[section] = {}
            scores = Score.objects.results(
                session_round.ranking_round,
                category=session_round.category,
            ).select_related()
            seedings = Seeding.objects.filter(entry__competition=self.competition).select_related()
            scores_by_comp_entry = {score.target.session_entry.competition_entry_id: score for score in scores}
            these_results = []
            for seed in seedings:
                score = scores_by_comp_entry.get(seed.entry_id, None)
                if not score:
                    continue
                score.placing = seed.seed
                these_results.append(score)
            results[section][session_round.category] = sorted(these_results, key=lambda s: s.placing)
        return self.render_to_pdf({'results': results})


@class_view_decorator(login_required)
class OlympicInput(TemplateView):
    template_name = 'olympic/input.html'

    labels = ['Bronze', 'Final', 'Semi', '1/4', '1/8', '1/16', '1/32', '1/64']

    def dispatch(self, request, slug, seed_pk):
        self.competition = get_object_or_404(Competition, slug=slug)
        self.seed = get_object_or_404(Seeding.objects.select_related(), pk=seed_pk)
        self.results = self.seed.result_set.all()
        highest_level = Match.objects.filter(session_round=self.seed.session_round).order_by('-level')[0].level
        self.forms = []
        for i in range(1, highest_level + 1):
            try:
                match = Match.objects.match_for_seed(self.seed, i)
            except Match.DoesNotExist:
                match = None
            if match:
                try:
                    instance = Result.objects.get(match=match, seed=self.seed)
                except Result.DoesNotExist:
                    instance = Result(match=match, seed=self.seed)
                form = ResultForm(instance=instance, data=request.POST if request.method == 'POST' else None, prefix='level-%s' % i)
            else:
                form = None
            self.forms.insert(0, {
                'form': form,
                'match': match,
                'label': self.labels[match.level] if match else None,
            })
        bronze = Match.objects.get(session_round=self.seed.session_round, level=1, match=2)
        try:
            instance = Result.objects.get(match=bronze, seed=self.seed)
        except Result.DoesNotExist:
            instance = Result(match=bronze, seed=self.seed)
        form = ResultForm(instance=instance, data=request.POST if request.method == 'POST' else None, prefix='bronze')
        self.forms.append({
            'form': form,
            'match': bronze,
            'label': self.labels[0],
        })
        return super(OlympicInput, self).dispatch(request, slug, seed_pk)

    def get_context_data(self):
        return {
            'competition': self.competition,
            'seed': self.seed,
            'results': self.results,
            'forms': self.forms,
        }

    def post(self, request, *args, **kwargs):
        for form in self.forms:
            if form['form']:
                if form['form'].is_valid():
                    form['form'].save()
                elif form['form'].instance.pk:
                    form['form'].instance.delete()
        return HttpResponseRedirect(reverse('olympic_index', kwargs={'slug': self.competition.slug}))


@class_view_decorator(login_required)
class OlympicScoreSheet(ScoreSheetsPdf):
    box_size = 0.35 * inch
    wide_box = box_size * 1.3
    title_position = 30

    match_names = [
            'Final / Bronze',
            'Semi Final',
            'Quarter Final',
            '1/8 Round',
            '1/16 Round',
            '1/32 Round',
            '1/64 Round',
    ]

    def set_options(self, slug=None, round_id=None):
        if slug:
            self.competition = get_object_or_404(Competition, slug=slug)
        if round_id:
            self.session_round = get_object_or_404(OlympicSessionRound, pk=round_id)
            if self.competition.sponsors.exists():
                highest_round = self.session_round.match_set.aggregate(highest=Max('level'))['highest']
                if highest_round >= 7:
                    self.do_sponsors = False

    def update_style(self):
        super(OlympicScoreSheet, self).update_style()
        self.col_widths = 3 * [self.box_size] + 3 * [self.wide_box] + [self.box_size * 3, self.box_size]
        self.row_heights = 8 * [self.box_size * 0.85]

    def setMargins(self, doc):
        doc.topMargin = 0.4 * inch
        doc.bottomMargin = 0.2 * inch

    def get_elements(self):
        elements = []
        seedings = self.session_round.seeding_set.select_related().order_by('seed')
        highest_seed = list(seedings)[-1].seed
        for seeding in seedings:
            entry = seeding.entry
            header_table_data = [
                [self.Para(entry.archer, 'h2'), self.Para(entry.club.name, 'h2')],
                [self.Para(u'{0} {1}'.format(entry.archer.get_gender_display(), entry.bowstyle), 'h2'), self.Para(u'Seed {0}'.format(seeding.seed), 'h2')],
            ]

            header_table = Table(header_table_data, [3 * inch, 4 * inch])

            matches = Match.objects.matches_for_seed(seeding, highest_seed=highest_seed)

            score_sheet_elements = []
            for i in range(len(matches)):
                match, timing = matches[i]
                match_title = self.Para(self.match_names[i], 'h3')
                if match and i > 0:
                    boss = self.Para('T. {0}'.format(match), 'h3')
                elif match:
                    boss = self.Para('T. {0} / {1}'.format(match, match + 2), 'h3')
                else:
                    boss = None
                if timing is not None:
                    timing = self.Para('Pass %s' % 'xABCDEFGHIJK'[timing], 'h3')
                table_data = [
                        [match_title, None, None, None, boss, None, timing, None],
                        ['Arrows' if match else self.Para('BYE', 'h3'), None, None, 'S',
                            'Pts' if self.session_round.shot_round.match_type == 'T' else 'RT',
                            'RT' if self.session_round.shot_round.match_type == 'T' else 'Opp.S',
                            'Opponent seed', None],
                        [None] * 6 + ['Your Signature', None],
                        [None] * 8,
                        [None] * 6 + ['Opponent Signature', None],
                        [None] * 8,
                        [None] * 6 + ['Win?', None],
                        ['Shoot-off', None, None, 'Total', None, 'Opponent Total', None, None],
                ]
                score_sheet = Table(table_data, self.col_widths, self.row_heights)
                score_sheet.setStyle(self.scores_table_style if match else self.bye_style)

                score_sheet_elements.append(score_sheet)

            table_of_score_sheets = []
            while len(score_sheet_elements) >= 2:
                table_of_score_sheets.append((score_sheet_elements.pop(), score_sheet_elements.pop()))
            if len(score_sheet_elements):
                table_of_score_sheets.append((score_sheet_elements.pop(), Spacer(self.box_size, self.box_size)))

            table_of_score_sheets = Table(table_of_score_sheets)
            table_of_score_sheets.setStyle(self.big_table_style)

            elements.append(KeepTogether([header_table, table_of_score_sheets]))
            elements.append(PageBreak())
        return elements

    scores_table_style = TableStyle([
        # alignment
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        ('BOX', (0, 0), (-1, -1), 2, colors.black),

        # wrapping grid
        ('BOX', (0, 1), (5, -2), 2, colors.black),
        ('INNERGRID', (0, 1), (5, -2), 0.25, colors.black),

        # arrows grid
        ('BOX', (0, 2), (2, -2), 2, colors.black),

        # totals grid
        ('BOX', (3, 1), (5, 1), 2, colors.black),
        ('BOX', (3, 2), (5, -2), 2, colors.black),
        ('BOX', (0, -1), (-1, -1), 2, colors.black),
        ('INNERGRID', (0, -1), (-1, -1), 2, colors.black),

        # details
        ('BOX', (6, 1), (7, -2), 2, colors.black),
        ('INNERGRID', (6, 1), (7, -2), 2, colors.black),

        # spans
        ('SPAN', (0, 0), (3, 0)),
        ('SPAN', (4, 0), (5, 0)),
        ('SPAN', (6, 0), (7, 0)),
        ('SPAN', (0, 1), (2, 1)),
        ('SPAN', (0, -1), (1, -1)),
        ('SPAN', (5, -1), (6, -1)),
        ('SPAN', (6, 2), (7, 2)),
        ('SPAN', (6, 3), (7, 3)),
        ('SPAN', (6, 4), (7, 4)),
        ('SPAN', (6, 5), (7, 5)),
    ])

    bye_style = TableStyle([
        # alignment
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ('BOX', (0, 0), (-1, 0), 2, colors.black),
        ('SPAN', (0, 0), (-1, 0)),
        ('SPAN', (0, 1), (-1, -1)),
    ])

    big_table_style = TableStyle([
        # alignment
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ])


@class_view_decorator(login_required)
class OlympicResults(HeadedPdfView):
    title = 'Results'

    match_headers = ['1/64', '1/32', '1/16', '1/8', 'QF', 'SF', 'F']

    def update_style(self):
        self.styles['h1'].alignment = 1
        self.styles['h2'].alignment = 1

    def setMargins(self, doc):
        doc.bottomMargin = 1.5 * inch

    def format_results(self, results, total_levels):
        results = results.reverse()
        max_level = results[0].match.level
        return ['BYE'] * (total_levels - max_level) + [result.display() for result in results]

    def get_elements(self):
        elements = []
        olympic_rounds = OlympicSessionRound.objects.filter(session__competition=self.competition).order_by('shot_round__distance', 'category')

        for olympic_round in olympic_rounds:
            elements += self.get_round_elements(olympic_round)

        return elements

    def get_round_elements(self, olympic_round):

        results = olympic_round.get_results()
        elements = []

        total_levels = results.total_levels

        table_headers = ['Rank', 'Seed', 'Name'] + self.match_headers[-total_levels:]
        table_data = [table_headers]

        for seeding in results.results:
            table_data.append([
                seeding.rank,
                seeding.seed,
                seeding.entry.archer.name,
            ] + self.format_results(seeding.results, total_levels))

        table = Table(table_data)
        table.setStyle(self.table_style)
        elements.append(KeepTogether([
            self.Para(u'{1}m: {0}'.format(olympic_round.category.name, olympic_round.shot_round.distance), 'h2'),
            table,
        ]))
        return elements

    table_style = TableStyle((
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 0), (1, -1), 'CENTER'),

        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEAFTER', (0, 0), (-2, -1), 0.5, colors.black),
    ))


@class_view_decorator(login_required)
class OlympicTree(OlympicResults):

    PAGE_HEIGHT = defaultPageSize[0]
    PAGE_WIDTH = defaultPageSize[1]
    do_sponsors = False

    def setMargins(self, doc):
        doc.bottomMargin = 0.4 * inch

    @property
    def match_cols(self):
        return [i for i in range(self.cols) if i % 3 is 0]

    def get_table_style(self):
        properties = [
            ('SIZE', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),

            ('LINEAFTER', (2, 0), (2, -1), 1, colors.black),
            ('LINEBELOW', (0, -1), (2, -1), 1, colors.black),
        ]
        vert_line = None
        for i in self.match_cols:

            offset = 2 ** (i / 3 - 1) if i else 0

            for j in range(self.rows):
                if (not i == 0 and not j % 2 ** (i / 3)) or (i == 0 and not j % 2):
                    properties.append(
                        ('LINEABOVE', (i, j + offset), (i + 2, j + offset), 1, colors.black),
                    )
                    if vert_line is not None:
                        properties.append(
                            ('LINEAFTER', (i + 2, vert_line + offset), (i + 2, j + offset - 1), 1, colors.black)
                        )
                        vert_line = None
                    else:
                        vert_line = j

        return TableStyle(properties)

    def match_blocks(self, level):
        nmatches = 2 ** (level - 1)
        block_size = self.rows / nmatches
        offset = self.rows / (2 ** (level + 1))
        blocks = [(i * block_size + offset, (i + 1) * block_size - offset) for i in range(nmatches)]
        return blocks

    def name_rows(self, col):
        level = self.total_levels - col / 3
        rows = []
        for start, end in self.match_blocks(level):
            rows += [start, end - 1]
        return rows

    def get_round_elements(self, olympic_round):

        elements = []
        self.total_levels = olympic_round.match_set.aggregate(Max('level'))['level__max']
        seedings = olympic_round.seeding_set.select_related('entry__archer')
        seedings_dict = {s.seed: s for s in seedings}

        self.rows = 2 ** self.total_levels
        self.cols = 3 * self.total_levels

        table_data = [[None for i in range(self.cols)] for j in range(self.rows)]

        for i in self.match_cols:
            level = self.total_levels - i / 3
            blocks = self.match_blocks(level)
            matches = olympic_round.match_set.filter(level=level).order_by('target').prefetch_related(
                Prefetch('result_set', queryset=Result.objects.select_related())
            )
            if (len(blocks) / len(matches)) == 2:
                old_matches = matches
                matches = []
                for j in range(len(old_matches)):
                    if not j % 2:
                        matches += [None, old_matches[j], old_matches[j + 1], None]
            if (len(blocks) / len(matches)) == 4:
                old_matches = matches
                matches = []
                for j in range(len(old_matches)):
                    if not j % 2:
                        matches += [None, old_matches[j], None, None, None, None, old_matches[j + 1], None]
            for m in range(len(blocks)):
                match = matches[m]
                if match is None:
                    continue
                seeds = [match.match, (2 ** match.level) + 1 - match.match]
                if m % 2:
                    seeds.reverse()
                seeds_remaining = len(set(seeds).intersection(set(seedings_dict.keys())))
                if self.total_levels - match.level > 0 or seeds_remaining == 2:
                    table_data[blocks[m][0]][i + 1] = '              ' * 2
                    table_data[blocks[m][0]][i + 2] = 'Target: ' + str(match.target)
                    table_data[blocks[m][1] - 1][i + 2] = 'Target: ' + str(match.target)
                    if match.target_2:
                        table_data[blocks[m][1] - 1][i + 2] = 'Target: ' + str(match.target_2)
                    if seeds[0] in seedings_dict or level == self.total_levels:
                        table_data[blocks[m][0]][i] = str(seeds[0])
                    if seeds[1] in seedings_dict or level == self.total_levels:
                        table_data[blocks[m][1] - 1][i] = str(seeds[1])
                    if seeds[0] in seedings_dict:
                        table_data[blocks[m][0]][i + 1] = seedings_dict[seeds[0]].entry.archer.name
                        seedings_dict.pop(seeds[0])
                    if seeds[1] in seedings_dict:
                        table_data[blocks[m][1] - 1][i + 1] = seedings_dict[seeds[1]].entry.archer.name
                        seedings_dict.pop(seeds[1])
                results = match.result_set.all()
                if not results:
                    continue
                results = sorted(results, key=lambda r: Match.objects._effective_seed(r.seed.seed, level))
                if m % 2:
                    results.reverse()
                if len(results) == 1:
                    r = results[0]
                    seed = Match.objects._effective_seed(r.seed.seed, level)
                    if seed == seeds[0]:
                        results = [r, None]
                    else:
                        results = [None, r]
                if results[0]:
                    table_data[blocks[m][0]][i] = results[0].seed.seed
                    table_data[blocks[m][0]][i + 1] = results[0].seed.entry.archer
                    table_data[blocks[m][0]][i + 2] = results[0].display()
                if results[1]:
                    table_data[blocks[m][1] - 1][i] = results[1].seed.seed
                    table_data[blocks[m][1] - 1][i + 1] = results[1].seed.entry.archer
                    table_data[blocks[m][1] - 1][i + 2] = results[1].display()

        table = Table(table_data)
        table.setStyle(self.get_table_style())

        elements.append(KeepTogether([
            self.Para(u'{1}m: {0}'.format(olympic_round.category.name, olympic_round.shot_round.distance), 'h2'),
            table,
        ]))
        return elements


@class_view_decorator(login_required)
class FieldPlan(FieldPlanMixin, HeadedPdfView):
    title = 'Field plan'
    PAGE_HEIGHT = defaultPageSize[0]
    PAGE_WIDTH = defaultPageSize[1]
    do_sponsors = False

    def setMargins(self, doc):
        doc.bottomMargin = 0.4 * inch

    def get_elements(self):
        field_plan = self.get_field_plan()
        widths = [35] + [11] * (len(field_plan[0]) - 1)
        table_style = self.get_table_style(field_plan)
        table_data = [[None] + field_plan[0][1:]]
        for row in field_plan[1:]:
            table_row = [row[0]]
            for target in row[1:]:
                if target.get('width'):
                    table_row.append('%s\n%s' % (target['category'].code(), target['level']))
                elif target.get('category') or not target:
                    table_row.append(None)
                else:
                    table_row.append(target)
            table_data.append(table_row)
        table = Table(table_data, colWidths=widths)
        table.setStyle(table_style)
        return [Spacer(0.5 * inch, 0.5 * inch), table]

    def get_table_style(self, data):
        table_style = [
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('SIZE', (0, 0), (-1, -1), 8),

            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (0, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, 0), 1, colors.black),
        ]
        for j, row in enumerate(data[1:], 1):
            for i, target in enumerate(row[1:], 1):
                if target.get('width', 0):
                    table_style.append(('SPAN', (i, j), (i + target['width'] - 1, j)))
                if not target:
                    table_style.append(('BACKGROUND', (i, j), (i, j), colors.lightgrey))
        return table_style
