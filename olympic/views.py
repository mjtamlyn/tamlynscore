from django.core.urlresolvers import reverse
from django.db.models import Max, Prefetch
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, TemplateView, FormView
from django.shortcuts import get_object_or_404, redirect

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import KeepTogether, PageBreak, Spacer, Table, TableStyle
from reportlab.rl_config import defaultPageSize

from entries.views import CompetitionMixin, ScoreSheetsPdf, HeadedPdfView
from scores.models import Score
from scores.result_modes import H2HSeedings
from scores.views import ResultModeMixin
from olympic.models import OlympicSessionRound, Seeding, Match, Result
from olympic.forms import ResultForm, SetupForm


class OlympicMixin(CompetitionMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'rounds': OlympicSessionRound.objects.filter(session__competition=self.competition),
        })
        return context


class OlympicIndex(OlympicMixin, ResultModeMixin, TemplateView):
    template_name = 'olympic_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scores = self.get_scores()
        mode = H2HSeedings(include_distance_breakdown=False, hide_golds=False)
        results = mode.get_results(self.competition, scores)
        for section in results:
            for category in results[section]:
                for score in results[section][category]:
                    score.details = mode.score_details(score, section)
                    if getattr(score, 'team', None):
                        for archer in score.team:
                            archer.details = mode.score_details(archer, section)
        context.update({
            'results': results,
        })
        return context

    def post(self, request, slug):
        session_round = OlympicSessionRound.objects.get(pk=request.POST['form-id'].replace('confirm-seedings-', ''))
        if 'remove-all' in request.POST:
            session_round.seeding_set.all().delete()
        else:
            score_ids = map(lambda s: int(s.replace('score-', '')), filter(lambda s: s.startswith('score-'), request.POST))
            scores = Score.objects.filter(target_id__in=score_ids)
            mode = H2HSeedings(include_distance_breakdown=False, hide_golds=False)
            results = mode.get_results(self.competition, scores)
            categories = list(results.values())
            seedings = []
            while not seedings:
                for category in categories:
                    if category:
                        seedings = list(category.values())[0]
                        if seedings:
                            break
                break
            session_round.set_seedings(seedings)
        return redirect('olympic_index', slug=self.competition.slug)


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
        max_target = (max(matches, key=lambda m: m.target)).target
        if matches[0].session_round.shot_round.team_type:
            max_target += 1
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


class OlympicSetup(OlympicMixin, FieldPlanMixin, FormView):
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


class OlympicInputIndex(OlympicMixin, DetailView):
    template_name = 'olympic/input_index.html'
    model = OlympicSessionRound
    pk_url_kwarg = 'round_id'
    context_object_name = 'round'
    labels = ['Bronze', 'Final', 'Semi', '1/4', '1/8', '1/16', '1/32', '1/64']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        highest_level = Match.objects.filter(session_round=self.object).order_by('-level')[0].level
        seedings = self.object.seeding_set.select_related('entry', 'entry__archer').order_by('seed')
        matches = self.object.match_set.prefetch_related('result_set')
        lookup = {}
        for match in matches:
            for result in match.result_set.all():
                lookup[(result.seed_id, match.level, match.match)] = result
        for seeding in seedings:
            results = []
            for level in range(1, highest_level + 1):
                match_number = Match.objects._match_number_for_seed(seeding.seed, level)
                result = lookup.get((seeding.pk, level, match_number))
                results.append(result)
            seeding.results = list(reversed(results))
            result = lookup.get((seeding.pk, 1, 2))
            seeding.results.append(result)
        context.update({
            'seedings': seedings,
            'levels': reversed(self.labels[:highest_level + 1]),
        })
        return context


class OlympicInput(OlympicMixin, TemplateView):
    template_name = 'olympic/input.html'

    labels = ['Bronze', 'Final', 'Semi', '1/4', '1/8', '1/16', '1/32', '1/64']

    def get_forms(self):
        self.seed = get_object_or_404(Seeding.objects.select_related(), pk=self.kwargs['seed_pk'])
        self.results = self.seed.result_set.all()
        highest_level = Match.objects.filter(session_round=self.seed.session_round).order_by('-level')[0].level
        forms = []
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
                form = ResultForm(instance=instance, data=self.request.POST if self.request.method == 'POST' else None, prefix='level-%s' % i)
            else:
                form = None
            forms.insert(0, {
                'form': form,
                'match': match,
                'label': self.labels[match.level] if match else None,
            })
        bronze = Match.objects.get(session_round=self.seed.session_round, level=1, match=2)
        try:
            instance = Result.objects.get(match=bronze, seed=self.seed)
        except Result.DoesNotExist:
            instance = Result(match=bronze, seed=self.seed)
        form = ResultForm(instance=instance, data=self.request.POST if self.request.method == 'POST' else None, prefix='bronze')
        forms.append({
            'form': form,
            'match': bronze,
            'label': self.labels[0],
        })
        return forms

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = self.get_forms()
        context.update({
            'seed': self.seed,
            'results': self.results,
            'forms': forms,
        })
        return context

    def post(self, request, *args, **kwargs):
        forms = self.get_forms()
        for form in forms:
            if form['form']:
                if form['form'].is_valid():
                    form['form'].save()
                elif form['form'].instance.pk:
                    form['form'].instance.delete()
        return HttpResponseRedirect(reverse('olympic_input_index', kwargs={'slug': self.competition.slug, 'round_id': self.seed.session_round_id}))


class OlympicScoreSheet(ScoreSheetsPdf):
    box_size = 0.32 * inch
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
        if round_id:
            self.session_round = get_object_or_404(OlympicSessionRound, pk=round_id)
            if self.competition.sponsors.exists():
                highest_round = self.session_round.match_set.aggregate(highest=Max('level'))['highest']
                if highest_round >= 7:
                    self.do_sponsors = False

    def update_style(self):
        super(OlympicScoreSheet, self).update_style()
        arrows = self.session_round.shot_round.arrows_per_end
        ends = self.session_round.shot_round.ends
        total_cols = 3 if self.session_round.shot_round.match_type == 'T' else 2
        self.col_widths = arrows * [self.box_size] + total_cols * [self.wide_box] + [self.box_size * 3.2, self.wide_box]
        self.row_heights = (3 + ends) * [self.box_size]

    def setMargins(self, doc):
        doc.topMargin = 0.4 * inch
        doc.bottomMargin = 0.2 * inch

    def get_elements(self):
        elements = []
        seedings = self.session_round.seeding_set.select_related().order_by('seed')
        highest_seed = list(seedings)[-1].seed
        for seeding in seedings:
            entry = seeding.entry
            header_table_data = []
            if self.session_round.shot_round.team_type:
                header_table_data.append([self.Para(seeding.label(), 'h2'), None])
            else:
                header_table_data.append([self.Para(entry.archer, 'h2'), self.Para(entry.team_name(), 'h2')])
            header_table_data.append([
                self.Para(self.session_round.category.name, 'h2'),
                self.Para(u'Seed {0}'.format(seeding.seed), 'h2'),
            ])
            header_table = Table(header_table_data, [3 * inch, 4 * inch])
            if self.session_round.shot_round.team_type:
                header_table.setStyle(TableStyle([
                    ('SPAN', (0, 0), (-1, 0)),
                ]))

            matches = Match.objects.matches_for_seed(seeding, highest_seed=highest_seed)

            score_sheet_elements = []
            for i in range(len(matches)):
                match, timing = matches[i]
                match_title = self.Para(self.match_names[i], 'h3')
                if match and i > 0:
                    boss = 'T.{}'.format(match)
                elif match:
                    boss = 'T.{0}/{1}'.format(match, match + 2)
                else:
                    boss = None
                if timing is not None:
                    timing = 'Pass %s' % 'ABCDEFGHIJK'[timing - 1]
                arrows = self.session_round.shot_round.arrows_per_end
                total_cols = 3 if self.session_round.shot_round.match_type == 'T' else 2
                ends = self.session_round.shot_round.ends
                table_data = [
                    [match_title] + [None] * arrows + [self.Para('{} {}'.format(boss, timing), 'h3')],
                    ['Arrows' if match else self.Para('BYE', 'h3')] + [None] * (arrows - 1) + [
                        'S',
                        'Pts' if self.session_round.shot_round.match_type == 'T' else 'RT',
                    ] + (['RT'] if self.session_round.shot_round.match_type == 'T' else []) + [
                        'Opponent seed',
                        None
                    ],
                    [None] * (arrows + total_cols) + ['Your Signature', None],
                    [None] * (arrows + total_cols + 2),
                    [None] * (arrows + total_cols) + ['Opponent Signature', None],
                    [None] * (arrows + total_cols + 2),
                ]
                if ends == 5:
                    table_data += [
                        [None] * (arrows + total_cols) + [None, None],
                    ]
                table_data += [
                    ['Shoot-off'] + [None] * (arrows - 1) + ['Total', None, 'Opponent Total'] + [None] * (total_cols - 1)
                ]
                score_sheet = Table(table_data, self.col_widths, self.row_heights)
                score_sheet.setStyle(self.get_scores_table_style(self.session_round.shot_round) if match else self.bye_style)

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

    def get_scores_table_style(self, shot_round):
        arrows = shot_round.arrows_per_end
        ends = shot_round.ends
        total_cols = 3 if self.session_round.shot_round.match_type == 'T' else 2
        shoot_off_arrows = 1
        if self.session_round.shot_round.team_type == 'X':
            shoot_off_arrows = 2
        if self.session_round.shot_round.team_type == 'T':
            shoot_off_arrows = 3
        rules = [
            # alignment
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            ('BOX', (0, 0), (-1, -1), 2, colors.black),

            # wrapping grid
            ('BOX', (0, 1), (arrows + total_cols - 1, -2), 2, colors.black),
            ('INNERGRID', (0, 1), (arrows + total_cols - 1, -2), 0.25, colors.black),

            # arrows grid
            ('BOX', (0, 2), (arrows - 1, -2), 2, colors.black),

            # totals grid
            ('BOX', (arrows, 1), (arrows + total_cols - 1, 1), 2, colors.black),
            ('BOX', (arrows, 2), (arrows + total_cols - 1, -2), 2, colors.black),
            ('BOX', (0, -1), (-1, -1), 2, colors.black),
            ('INNERGRID', (0, -1), (-1, -1), 2, colors.black),

            # details
            ('BOX', (arrows + total_cols, 1), (arrows + total_cols + 1, -2), 2, colors.black),
            ('INNERGRID', (arrows + total_cols, 1), (arrows + total_cols + 1, -2), 2, colors.black),

            # spans
            ('SPAN', (0, 0), (arrows, 0)),
            ('SPAN', (arrows + 1, 0), (-1, 0)),
            ('SPAN', (0, 1), (arrows - 1, 1)),
            ('SPAN', (0, -1), (arrows - (shoot_off_arrows + 1), -1)),
            ('SPAN', (arrows + 2, -1), (arrows + total_cols, -1)),
            ('SPAN', (arrows + total_cols, 2), (arrows + total_cols + 1, 2)),
            ('SPAN', (arrows + total_cols, 3), (arrows + total_cols + 1, 3)),
            ('SPAN', (arrows + total_cols, 4), (arrows + total_cols + 1, 4)),
            ('SPAN', (arrows + total_cols, 5), (arrows + total_cols + 1, 5)),
        ]
        if ends == 5:
            rules += [
                ('SPAN', (arrows + total_cols, -2), (arrows + total_cols + 1, -2)),
                ('BACKGROUND', (arrows + total_cols, -2), (arrows + total_cols + 1, -2), colors.lightgrey),
            ]
        return TableStyle(rules)

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


class OlympicResults(CompetitionMixin, HeadedPdfView):
    admin_required = False
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
                seeding.label(),
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


class OlympicTree(OlympicResults):
    admin_required = False

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

            offset = int(2 ** (i / 3 - 1)) if i else 0

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
        level = int(level)
        nmatches = 2 ** (level - 1)
        block_size = int(self.rows / nmatches)
        if level == self.total_levels:
            offset = 0
        else:
            offset = 2 ** (self.total_levels - level - 1)
        blocks = [(i * block_size + offset, (i + 1) * block_size - offset) for i in range(nmatches)]
        return blocks

    def get_round_elements(self, olympic_round):

        elements = []
        self.total_levels = olympic_round.match_set.aggregate(Max('level'))['level__max']
        seedings = olympic_round.seeding_set.select_related('entry__archer')
        seedings_dict = {s.seed: s for s in seedings}

        self.rows = 2 ** self.total_levels
        self.cols = 3 * self.total_levels

        table_data = [[None for i in range(self.cols)] for j in range(self.rows)]

        previous_matches = None

        for i in self.match_cols:
            level = self.total_levels - i / 3
            blocks = self.match_blocks(level)
            matches = olympic_round.match_set.filter(level=level).order_by('timing', 'target').prefetch_related(
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
                    if not j % 4:
                        if not j % 8:
                            matches += [None, old_matches[j], None, None]
                        else:
                            matches += [None, None, old_matches[j], None]
            if (len(blocks) / len(matches) * 3) == 4:
                old_matches = matches
                matches = []
                for j in range(len(old_matches)):
                    if not j % 4:
                        if not j % 8:
                            matches += [None, old_matches[j], old_matches[j + 1], old_matches[j + 2]]
                        else:
                            matches += [old_matches[j], old_matches[j + 1], old_matches[j + 2], None]
            for m in range(len(blocks)):
                try:
                    match = matches[m]
                except IndexError:
                    match = None
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
                        table_data[blocks[m][0]][i + 1] = seedings_dict[seeds[0]].label()
                        seedings_dict.pop(seeds[0])
                    if seeds[1] in seedings_dict:
                        table_data[blocks[m][1] - 1][i + 1] = seedings_dict[seeds[1]].label()
                        seedings_dict.pop(seeds[1])
                results = match.result_set.all()
                if results:
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
                        table_data[blocks[m][0]][i + 1] = results[0].seed.label()
                        table_data[blocks[m][0]][i + 2] = results[0].display()
                    if results[1]:
                        table_data[blocks[m][1] - 1][i] = results[1].seed.seed
                        table_data[blocks[m][1] - 1][i + 1] = results[1].seed.label()
                        table_data[blocks[m][1] - 1][i + 2] = results[1].display()
                elif previous_matches:
                    qualified_seeds = []
                    for previous in previous_matches:
                        for r in previous.result_set.all():
                            if Match.objects._effective_seed(r.seed.seed, level) in seeds and r.win:
                                qualified_seeds.append(r)
                    if not qualified_seeds:
                        continue
                    if len(qualified_seeds) == 1:
                        r = qualified_seeds[0]
                        seed = Match.objects._effective_seed(r.seed.seed, level)
                        if seed == seeds[0]:
                            qualified_seeds = [r, None]
                        else:
                            qualified_seeds = [None, r]
                    if qualified_seeds[0]:
                        table_data[blocks[m][0]][i] = qualified_seeds[0].seed.seed
                        table_data[blocks[m][0]][i + 1] = qualified_seeds[0].seed.label()
                    if qualified_seeds[1]:
                        table_data[blocks[m][1] - 1][i] = qualified_seeds[1].seed.seed
                        table_data[blocks[m][1] - 1][i + 1] = qualified_seeds[1].seed.label()
                else:
                    continue

            # Set up the previous matches so we can carry that data through
            previous_matches = matches

        table = Table(table_data)
        table.setStyle(self.get_table_style())

        elements.append(KeepTogether([
            self.Para(u'{1}m: {0}'.format(olympic_round.category.name, olympic_round.shot_round.distance), 'h2'),
            table,
        ]))
        return elements


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
