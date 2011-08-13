from django.contrib.auth.decorators import login_required
from django.db.models import Min, Max
from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import render, get_object_or_404

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import KeepTogether, PageBreak, Spacer, Table, TableStyle

from entries.models import Competition
from entries.views import ScoreSheetsPdf, HeadedPdfView
from scores.models import Score
from olympic.models import OlympicSessionRound, Seeding, Match

from itertools import groupby

class OlympicIndex(View):
    def get(self, request, slug):
        competition = get_object_or_404(Competition, slug=slug)
        session_rounds = OlympicSessionRound.objects.filter(session__competition=competition).order_by('session__start')
        session_info = [(
            session_round.session,
            session_round,
            session_round.seeding_set.all(),
            Score.objects.results(session_round.ranking_round, leaderboard=True, category=session_round.category),
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
        print scores
        session_round.set_seedings(scores)
        return self.get(request, slug)

olympic_index = login_required(OlympicIndex.as_view())

class OlympicScoreSheet(ScoreSheetsPdf):

    match_names = [
            'Final / Bronze',
            'Semi Final',
            'Quarter Final',
            '1/8 Round',
            '1/16 Round',
            '1/32 Round',
    ]

    def set_options(self, slug=None, round_id=None):
        if slug:
            self.competition = get_object_or_404(Competition, slug=slug)
        if round_id:
            self.session_round = get_object_or_404(OlympicSessionRound, pk=round_id)

    def update_style(self):
        super(OlympicScoreSheet, self).update_style()
        self.col_widths = 3 * [self.box_size] + 3 * [self.wide_box] + 2 * [self.box_size * 1.85]
        self.row_heights = 8 * [self.box_size]

    def setMargins(self, doc):
        doc.bottomMargin = 0.3*inch

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

            header_table = Table(header_table_data, [2*inch, 4*inch])

            matches = Match.objects.matches_for_seed(seeding, highest_seed=highest_seed)

            score_sheet_elements = []
            for i in range(len(matches)):
                match = matches[i]
                match_title = self.Para(self.match_names[i], 'h3')
                if match and i > 0:
                    boss = self.Para('Target {0}'.format(match), 'h3') 
                elif match:
                    boss = self.Para('T. {0} / {1}'.format(match, match + 2), 'h3')
                else:
                    boss = None
                table_data = [
                        [match_title, None, None, None, boss, None, self.Para('Opponent', 'h3'), None],
                        ['Arrows' if match else self.Para('BYE', 'h3'), None, None, 'S',
                            'Pts' if self.session_round.shot_round.match_type == 'T' else 'RT',
                            'RT' if self.session_round.shot_round.match_type == 'T' else 'Opp.S',
                            self.Para('Seed', 'h3'), None],
                        [None] * 6 + ['Your Signature', None],
                        [None] * 8,
                        [None] * 6 + ['Opponent Signature', None],
                        [None] * 8,
                        [None] * 6 + ['Win?', None],
                        ['Shoot-off', None,  None, 'Total', None, 'Opponent Total', None, None],
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
        ('BOX', (6, 0), (7, -2), 2, colors.black),
        ('INNERGRID', (6, 1), (7, -2), 2, colors.black),
        ('LINEABOVE', (7, 1), (7, 1), 2, colors.black),

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
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ])

olympic_score_sheet = login_required(OlympicScoreSheet.as_view())

class OlympicResults(HeadedPdfView):
    title = 'Head To Head Results'

    match_headers = ['1/32', '1/16', '1/8', 'QF', 'SF', 'F']

    def update_style(self):
        self.styles['h1'].alignment = 1
        self.styles['h2'].alignment = 1

    def setMargins(self, doc):
        doc.bottomMargin = 0.3*inch

    def pretty_rank(self, rank):
        if rank <= 8:
            return rank
        real_rank = 8
        while real_rank < rank:
            real_rank = real_rank * 2
        return real_rank/2 + 1

    def format_results(self, results, total_levels):
        results = results.reverse()
        max_level = results[0].match.level
        return ['BYE'] * (total_levels - max_level) + [result.total for result in results]
    
    def get_elements(self):
        elements = []
        olympic_rounds = OlympicSessionRound.objects.filter(session__competition=self.competition).order_by('shot_round__distance', 'category')

        for olympic_round in olympic_rounds:
            elements += self.get_round_elements(olympic_round)

        return elements

    def get_round_elements(self, olympic_round):

        elements = []
        seedings = olympic_round.seeding_set.all()
        total_levels = olympic_round.match_set.aggregate(Max('level'))['level__max']

        seedings_with_results = []
        for seeding in seedings:
            results = seeding.result_set.order_by('match__level')
            seedings_with_results.append((seeding, results))

        seedings_with_results = sorted(seedings_with_results, key=lambda s: (s[1][0].match.level, s[1][0].match.match if s[1][0].match.level == 1 else None, -s[1][0].total, s[0].seed))

        table_headers = ['Rank', 'Seed', 'Name'] + self.match_headers[-total_levels:]
        table_data = [table_headers] + [[
            self.pretty_rank(seedings_with_results.index((seeding, results)) + 1),
            seeding.seed,
            seeding.entry.archer.name,
        ] + self.format_results(results, total_levels)
            for seeding, results in seedings_with_results]
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

olympic_results = login_required(OlympicResults.as_view())

class OlympicTree(OlympicResults):
    pass

olympic_tree = login_required(OlympicTree.as_view())
