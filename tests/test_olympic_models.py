from django.test import TestCase

from olympic.models import Match

from .factories import (
    BowstyleFactory, CategoryFactory, MatchFactory, OlympicRoundFactory,
)


class TestOlympicRound(TestCase):

    def test_names(self):
        r = OlympicRoundFactory.create()
        self.assertTrue(str(r))
        self.assertTrue(r.short_name())

    def test_match_lengths(self):
        examples = (
            ('', 5, 3),  # Individual is 5x3
            ('T', 4, 6),  # Team is 4x6
            ('X', 4, 4),  # Mixed is 4x4
        )
        for (team_type, ends, arrows) in examples:
            r = OlympicRoundFactory(team_type=team_type)
            self.assertEqual(r.ends, ends)
            self.assertEqual(r.arrows_per_end, arrows)


class TestCategoryNames(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.rec = BowstyleFactory.create(name='Recurve')
        cls.bb = BowstyleFactory.create(name='Barebow')

    def test_rm(self):
        c = CategoryFactory.create(bowstyles=[self.rec], gender='G')
        self.assertEqual(c.name, 'Recurve Men')
        self.assertEqual(c.code, 'RM')
        self.assertEqual(str(c), 'Category: Recurve Men')

    def test_ungendered(self):
        c = CategoryFactory.create(bowstyles=[self.bb])
        self.assertEqual(c.name, 'Barebow')
        self.assertEqual(c.code, 'B')

    def test_age_group(self):
        c = CategoryFactory.create(bowstyles=[self.rec], gender='L', ages=['U18'])
        self.assertEqual(c.name, 'Recurve U18 Women')
        self.assertEqual(c.code, 'RU18W')

    def test_multiple_age_group(self):
        c = CategoryFactory.create(bowstyles=[self.rec], gender='L', ages=['U18', 'U16'])
        self.assertEqual(c.name, 'Recurve U18, U16 Women')
        self.assertEqual(c.code, 'RU18U16W')

    def test_multiple_bows(self):
        c = CategoryFactory.create(bowstyles=[self.rec, self.bb], gender='G')
        self.assertEqual(c.name, 'Recurve, Barebow Men')
        self.assertEqual(c.code, 'RBM')

    def test_novice(self):
        c = CategoryFactory.create(bowstyles=[self.rec], novice='N')
        self.assertEqual(c.name, 'Novice Recurve')
        self.assertEqual(c.code, 'NR')


class TestMatch(TestCase):

    def test_repr(self):
        match = MatchFactory.create()
        self.assertTrue(str(match))

    def test_archers_per_round(self):
        sizes = (
            (1, 2, 1),
            (2, 4, 2),
            (3, 8, 4),
            (4, 16, 8),
            (5, 32, 16),
            (6, 64, 32),
            (7, 128, 64),
        )
        for level, archers, matches in sizes:
            match = MatchFactory(level=level)
            self.assertEqual(match.n_archers_this_round, archers)
            self.assertEqual(match.n_matches_this_round, matches)

    def test_matches_next_round(self):
        sizes = (
            (1, None, None),
            (2, 2, 1),
            (3, 4, 2),
            (4, 8, 4),
            (5, 16, 8),
            (6, 32, 16),
            (7, 64, 32),
        )
        for level, archers, matches in sizes:
            match = MatchFactory(level=level)
            self.assertEqual(match.n_archers_next_round, archers)
            self.assertEqual(match.n_matches_next_round, matches)

    def test_match_number_for_seed(self):
        examples = (
            (1, 1, 1),  # Final is match 1
            (23, 1, 1),  # Final is always match 1
            (1, 2, 1),  # Semi-finalists in the right place
            (2, 2, 2),
            (3, 2, 2),
            (4, 2, 1),
            (5, 2, 1),  # 5th becomes 4th
            (9, 2, 1),  # 9th becomes 8th becomes 1st
            (23, 2, 2),  # 23rd becomes 10th becomes 7th becomes 2nd
            # Quarter finals
            (1, 3, 1),
            (2, 3, 2),
            (3, 3, 3),
            (4, 3, 4),
            (5, 3, 4),
            (6, 3, 3),
            (7, 3, 2),
            (8, 3, 1),
            (9, 3, 1),  # 9th becomes 8th
        )
        for seed, level, match in examples:
            self.assertEqual(Match.objects.match_number_for_seed(seed, level), match)

    def test_effective_seed(self):
        # This builds on match_number so doesn't need as extensive testing
        # Instead we'll do a more complete run for seed 23
        examples = (
            (23, 6, 23),  # in 1/32, is the 23rd seed, and the higher seed
            (23, 5, 23),  # in 1/16, is the 23rd seed, now the lower seed
            (23, 4, 10),  # in 1/8, has beaten 10th seed
            (23, 3, 7),  # in Q, has beaten 7th seed
            (23, 2, 2),  # in S, has beaten 2nd seed
            (23, 2, 2),  # in F, continues as 2nd seed
        )
        for seed, level, effective in examples:
            self.assertEqual(Match.objects.effective_seed(seed, level), effective)

    def test_for_placing(self):
        examples = (
            (1, 1, 1),  # Final
            (1, 2, 3),  # Bronze
            (2, 1, 1),  # Semis
            (2, 2, 1),  # Semis
            (2, 4, 5),  # 5th semi
            (2, 8, 13),  # 13th semi
        )
        for level, match, placing in examples:
            m = MatchFactory(level=level, match=match)
            self.assertEqual(m.for_placing, placing)

    def test_effective_match(self):
        examples = (
            (1, 1, 1),  # Final
            (1, 2, 1),  # Bronze
            (1, 4, 1),  # 7th Final
            (2, 1, 1),  # Semi 1
            (2, 2, 2),  # Semi 2
            (2, 4, 2),  # 5th semi 2
            (2, 7, 1),  # 13th semi 1
        )
        for level, match, effective_match in examples:
            m = MatchFactory(level=level, match=match)
            self.assertEqual(m.effective_match, effective_match, 'Level %s, Match %s' % (level, match))

    def test_round_name_and_match(self):
        examples = (
            (1, 1, 'Final', 'Final'),
            (1, 2, 'Bronze', 'Bronze'),
            (1, 4, '7th Final', '7th Final'),
            (2, 1, 'Semis', 'Semis Match 1'),
            (2, 2, 'Semis', 'Semis Match 2'),
            (2, 4, '5th Semis', '5th Semis Match 2'),
            (2, 7, '13th Semis', '13th Semis Match 1'),
        )
        for level, match, round_name, match_name in examples:
            m = MatchFactory(level=level, match=match)
            self.assertEqual(m.round_name, round_name, 'Level %s, Match %s' % (level, match))
            self.assertEqual(m.match_name, match_name, 'Level %s, Match %s' % (level, match))
