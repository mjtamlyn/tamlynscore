import functools

from django.db.models import Max, Prefetch
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import DetailView, FormView, TemplateView

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate, Frame, KeepTogether, NextPageTemplate, PageBreak,
    PageTemplate, Spacer, Table, TableStyle,
)
from reportlab.rl_config import defaultPageSize

from entries.views import CompetitionMixin, HeadedPdfView, ScoreSheetsPdf
from olympic.forms import ResultForm, SetupForm
from olympic.match_loader import MatchLoader
from olympic.models import Match, OlympicSessionRound, Result, Seeding
from scores.models import Score
from scores.result_modes import H2HSeedings
from scores.views import ResultModeMixin, Results


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


class OlympicSetup(OlympicMixin, ResultModeMixin, FormView):
    form_class = SetupForm
    template_name = 'olympic/setup.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['session_rounds'] = self.session_rounds
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def post(self, *args, **kwargs):
        self.session_rounds = OlympicSessionRound.objects.filter(session__competition=self.competition)
        return super().post(*args, **kwargs)

    def get_context_data(self, **kwargs):
        matches = MatchLoader(self.competition)
        matches.load_all()
        self.session_rounds = matches.session_rounds

        context = super().get_context_data(**kwargs)

        scores = self.get_scores()
        mode = H2HSeedings(include_distance_breakdown=False, hide_golds=False)
        results = mode.get_results(self.competition, scores)
        numbers = []
        for (r, r_cat) in results.items():
            for (cat, entries) in r_cat.items():
                numbers.append([r, cat, len(entries)])
        context['numbers'] = numbers

        context['targets'] = matches.targets
        context['matches_by_spans'] = matches.matches_by_spans()

        return context

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
                match_number = Match.objects.match_number_for_seed(seeding.seed, level)
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
        super().update_style()
        arrows = self.session_round.shot_round.arrows_per_end
        ends = self.session_round.shot_round.ends
        total_cols = 3 if self.session_round.shot_round.match_type == 'T' else 2
        self.col_widths = arrows * [self.box_size] + total_cols * [self.wide_box] + [self.box_size * 3.2, self.wide_box]
        self.row_heights = (3 + ends) * [self.box_size]

    def setMargins(self, doc):
        doc.topMargin = 0.4 * inch
        doc.bottomMargin = 0.2 * inch
        doc.leftMargin = doc.rightMargin = 0.2 * inch

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
                if i == 0:
                    # Finals need special casing
                    # This is a final, potentially with no bronze match
                    # available for the top seed(s) if there are less than 3
                    # people
                    has_match = True
                    final_target, final_timing = matches[0]
                    try:
                        bronze_match = Match.objects.get(level=1, session_round=seeding.session_round, match=2)
                    except Match.DoesNotExist:
                        bronze_target = bronze_timing = None
                    else:
                        bronze_target, bronze_timing = bronze_match.target, bronze_match.timing
                        effective_seed = Match.objects.effective_seed(seeding.seed, 1)
                        if bronze_match.target_2 and effective_seed == 2:
                            bronze_target = bronze_match.target_2

                    if highest_seed <= 3:
                        match_title = 'Final'
                        location_label = 'T.{} Pass {}'.format(final_target, 'ABCDEFGHIJK'[final_timing - 1])
                    elif bronze_timing != final_timing:
                        match_title = self.match_names[0]
                        location_label = 'T.{} Pass {} / T.{} Pass {}'.format(
                            final_target,
                            'ABCDEFGHIJK'[final_timing - 1],
                            bronze_target,
                            'ABCDEFGHIJK'[bronze_timing - 1],
                        )
                    else:
                        match_title = self.match_names[0]
                        location_label = 'T.{} / T.{} Pass {}'.format(
                            final_target,
                            bronze_target,
                            'ABCDEFGHIJK'[final_timing - 1],
                        )
                else:
                    match, timing = matches[i]
                    has_match = bool(match)
                    match_title = self.match_names[i]
                    if match:
                        boss = 'T.{}'.format(match)
                    else:
                        boss = None
                    if timing is not None:
                        timing = 'Pass %s' % 'ABCDEFGHIJK'[timing - 1]
                    location_label = '{} {}'.format(boss, timing)

                arrows = self.session_round.shot_round.arrows_per_end
                total_cols = 3 if self.session_round.shot_round.match_type == 'T' else 2
                ends = self.session_round.shot_round.ends
                table_data = [
                    [self.Para(match_title, 'h3')] + [None] * arrows + [self.Para(location_label, 'h3')],
                    ['Arrows' if has_match else self.Para('BYE', 'h3')] + [None] * (arrows - 1) + [
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
                score_sheet.setStyle(self.get_scores_table_style(self.session_round.shot_round) if has_match else self.bye_style)

                score_sheet_elements.append(score_sheet)

            table_of_score_sheets = []
            if self.session_round.shot_round.arrows_per_end <= 4:
                while len(score_sheet_elements) >= 2:
                    table_of_score_sheets.append((score_sheet_elements.pop(), score_sheet_elements.pop()))
                if len(score_sheet_elements):
                    table_of_score_sheets.append((score_sheet_elements.pop(), Spacer(self.box_size, self.box_size)))
            else:
                while score_sheet_elements:
                    table_of_score_sheets.append((score_sheet_elements.pop(),))

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
    filename = 'H2H results'

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
            self.Para(u'{2} {1}m: {0}'.format(olympic_round.category.name, olympic_round.shot_round.distance, olympic_round.shot_round.get_team_type_display()), 'h2'),
            table,
        ]))
        return elements

    table_style = TableStyle((
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 0), (1, -1), 'CENTER'),

        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEAFTER', (0, 0), (-2, -1), 0.5, colors.black),
    ))


class OlympicTreeMixin(object):
    @property
    def match_cols(self):
        return [i for i in range(self.cols) if i % 3 == 0]

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

    def get_round_table(self, olympic_round):

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
            if len(blocks) != len(matches) and level != 1:
                old_matches = matches
                matches = [None] * int(level ** 2)
                layout = olympic_round._get_match_layout(int(level))
                for match in old_matches:
                    if match.match > len(layout):  # TODO: Ignore lower rankings for full ranked for now?
                        continue
                    index = layout.index(match.match)
                    matches[index] = match
            elif level == 1:
                # Handle when bronze and final are separated
                matches = list(filter(lambda m: m.match == 1, matches))
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
                if self.total_levels - match.level > 0 or seeds_remaining == 2 or (self.total_levels == match.level and not seedings):
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
                    results = sorted(results, key=lambda r: Match.objects.effective_seed(r.seed.seed, level))
                    if m % 2:
                        results.reverse()
                    if len(results) == 1:
                        r = results[0]
                        seed = Match.objects.effective_seed(r.seed.seed, level)
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
                    for previous in filter(None, previous_matches):
                        for r in previous.result_set.all():
                            if Match.objects.effective_seed(r.seed.seed, level) in seeds and r.win:
                                qualified_seeds.append(r)
                    if qualified_seeds:
                        if len(qualified_seeds) == 1:
                            r = qualified_seeds[0]
                            seed = Match.objects.effective_seed(r.seed.seed, level)
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

                if self.total_levels >= 2 and level == 1:
                    if self.total_levels == 3:
                        table_data.append([None for i in range(self.cols)])
                        table_data.append([None for i in range(self.cols)])
                    if self.total_levels == 4:
                        table_data.append([None for i in range(self.cols)])

                    bronze = olympic_round.match_set.filter(level=1, match=2)
                    if not bronze:
                        continue
                    bronze = bronze[0]
                    results = bronze.result_set.select_related()
                    results = sorted(results, key=lambda r: Match.objects.effective_seed(r.seed.seed, level))
                    if self.total_levels == 2:
                        table_data.append([''] * len(table_data[-1]))
                        table_data.append([''] * len(table_data[-1]))
                    table_data[-2][-2] = '              ' * 2
                    table_data[-2][-1] = 'Target: ' + str(bronze.target)
                    table_data[-1][-1] = 'Target: ' + str(bronze.target)
                    if match.target_2:
                        table_data[-1][-1] = 'Target: ' + str(bronze.target_2)

                    seeds = [1, 2]
                    if results:
                        if len(results) == 1:
                            r = results[0]
                            seed = Match.objects.effective_seed(r.seed.seed, level)
                            if seed == seeds[0]:
                                results = [r, None]
                            else:
                                results = [None, r]
                        if results[0]:
                            table_data[-2][-3] = results[0].seed.seed
                            table_data[-2][-2] = results[0].seed.label()
                            table_data[-2][-1] = results[0].display()
                        if results[1]:
                            table_data[-1][-3] = results[1].seed.seed
                            table_data[-1][-2] = results[1].seed.label()
                            table_data[-1][-1] = results[1].display()
                    elif previous_matches:
                        qualified_seeds = []
                        for previous in previous_matches:
                            for r in previous.result_set.all():
                                if Match.objects.effective_seed(r.seed.seed, level) in seeds and not r.win:
                                    qualified_seeds.append(r)
                        if not qualified_seeds:
                            continue
                        if len(qualified_seeds) == 1:
                            r = qualified_seeds[0]
                            seed = Match.objects.effective_seed(r.seed.seed, level)
                            if seed == seeds[0]:
                                qualified_seeds = [r, None]
                            else:
                                qualified_seeds = [None, r]
                        if qualified_seeds[0]:
                            table_data[-2][-3] = qualified_seeds[0].seed.seed
                            table_data[-2][-2] = qualified_seeds[0].seed.label()
                        if qualified_seeds[1]:
                            table_data[-1][-3] = qualified_seeds[1].seed.seed
                            table_data[-1][-2] = qualified_seeds[1].seed.label()

            # Set up the previous matches so we can carry that data through
            previous_matches = matches

        return table_data


class OlympicTree(OlympicTreeMixin, CompetitionMixin, TemplateView):
    template_name = 'olympic/tree.html'
    admin_required = False

    def add_borders(self, table, round):
        tree = []

        right_borders = []
        top_borders = []
        vert_line = None
        for i in self.match_cols:
            offset = int(2 ** (i / 3 - 1)) if i else 0

            for j in range((2 ** (len(table[0]) // 3)) + 1):
                if (not i == 0 and not j % 2 ** (i / 3)) or (i == 0 and not j % 2):
                    top_borders.append(((i, i + 2), j + offset))
                    if vert_line is not None:
                        right_borders.append((i + 2, (vert_line + offset, j + offset - 1)))
                        vert_line = None
                    else:
                        vert_line = j

        main_rows = 2 ** (len(table[0]) // 3)
        for i, row in enumerate(table):
            tree_row = []
            for j, cell in enumerate(row):
                borders = []
                for x, y in top_borders:
                    if j >= x[0] and j <= x[1] and i == y and i <= main_rows:
                        borders.append('border-top')
                if j >= len(row) - 3 and i == len(table) - 2:
                    borders.append('border-top')
                if j >= len(row) - 3 and i == len(table) - 1:
                    borders.append('border-bottom')
                # if not (j + 1) % 3:
                    # TODO
                    # if i in right_borders:
                    #     borders.append('border-right')
                tree_row.append((cell, ' '.join(borders)))
            tree.append(tree_row)
        return tree

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        olympic_rounds = OlympicSessionRound.objects.filter(session__competition=self.competition).order_by('id')
        rounds = []
        for round in olympic_rounds:
            table = self.get_round_table(round)
            tree = self.add_borders(table, round)
            rounds.append({
                'round': round,
                'tree': tree
            })
        context['rounds'] = rounds
        return context


class OlympicTreePdf(OlympicTreeMixin, OlympicResults):
    admin_required = False
    filename = 'H2H bracket'

    PAGE_HEIGHT = defaultPageSize[0]
    PAGE_WIDTH = defaultPageSize[1]
    do_sponsors = False

    def setMargins(self, doc):
        doc.bottomMargin = 0.4 * inch

    def get_table_style(self):
        properties = [
            ('SIZE', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),

            ('LINEAFTER', (2, 0), (2, self.rows - 1), 1, colors.black),
            ('LINEBELOW', (0, self.rows - 1), (2, self.rows - 1), 1, colors.black),
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

        if self.total_levels >= 3:
            properties += [
                ('LINEAFTER', (-1, -2), (-1, -1), 1, colors.black),
                ('LINEBELOW', (-3, -3), (-1, -3), 1, colors.black),
                ('LINEBELOW', (-3, -1), (-1, -1), 1, colors.black),
            ]

        return TableStyle(properties)

    def get_round_elements(self, olympic_round):
        table_data = self.get_round_table(olympic_round)

        table = Table(table_data)
        table.setStyle(self.get_table_style())

        elements = []
        elements.append(KeepTogether([
            self.Para(u'{2} {1}m: {0}'.format(olympic_round.category.name, olympic_round.shot_round.distance, olympic_round.shot_round.get_team_type_display()), 'h2'),
            table,
        ]))
        return elements


class FieldPlan(CompetitionMixin, HeadedPdfView):
    title = 'Field plan'
    PAGE_HEIGHT = defaultPageSize[0]
    PAGE_WIDTH = defaultPageSize[1]
    do_sponsors = False

    def setMargins(self, doc):
        doc.bottomMargin = 0.4 * inch

    def get_elements(self):
        matches = MatchLoader(self.competition)
        matches.load_all()
        spans = matches.matches_by_spans()

        widths = [35] + [20 if len(matches.targets) <= 32 else 11] * len(matches.targets)
        table_style = self.get_table_style(spans)
        table_data = [[None] + matches.targets]
        for timing in spans:
            table_row = [timing['name']]
            for target in timing['targets']:
                if target.get('span'):
                    table_row.append('%s\n%s' % (target['category_short'], target['round']))
                elif not target['match']:
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
        for j, timing in enumerate(data, 1):
            for i, target in enumerate(timing['targets'], 1):
                if target.get('span', 0):
                    table_style.append(('SPAN', (i, j), (i + target['span'] - 1, j)))
                if not target['match']:
                    table_style.append(('BACKGROUND', (i, j), (i, j), colors.lightgrey))
        return table_style


class CombinedPdf(CompetitionMixin, HeadedPdfView):
    title = 'Results'

    def get(self, request, **kwargs):
        self.set_options(**kwargs)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="%s Full Results Book.pdf"' % self.competition
        doc = self.get_doc(response)
        elements = []

        modes = self.competition.result_modes.filter(leaderboard_only=False)

        for mode in modes:
            seedings_view = Results(competition=self.competition, is_admin=self.is_admin, request=None, kwargs={'mode': mode.mode, 'format': 'pdf'})
            seedings_view.format = seedings_view.get_format()
            seedings_view.mode = seedings_view.get_mode()
            seedings_view.object_list = seedings_view.get_queryset()
            seedings_view.set_styles()
            context = seedings_view.get_context_data(object_list=seedings_view.object_list)
            elements += seedings_view.get_elements(context['results'])
            elements.append(PageBreak())

        results_view = OlympicResults(competition=self.competition)
        results_view.doc = doc
        results_view.update_style()
        elements += results_view.get_elements()

        elements.append(NextPageTemplate('Landscape'))
        tree_view = OlympicTreePdf(competition=self.competition)
        elements += tree_view.get_elements()

        doc.build(elements)
        return response

    def get_doc(self, response):
        doc = BaseDocTemplate(response, pagesize=(self.PAGE_WIDTH, self.PAGE_HEIGHT))
        doc._calc()
        portrait_frame = Frame(inch, inch, doc.width, doc.height, id='normal')
        landscape_frame = Frame(inch, inch, doc.height, doc.width, id='landscape')
        doc.addPageTemplates([
            PageTemplate(id='Portrait', frames=portrait_frame, onPage=self.draw_title, pagesize=doc.pagesize),
            PageTemplate(id='Landscape', frames=landscape_frame, onPage=functools.partial(self.draw_title, invert_dimensions=True), pagesize=[doc.pagesize[1], doc.pagesize[0]]),
        ])
        return doc
