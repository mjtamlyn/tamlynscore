import math

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.functional import cached_property

from core.models import (
    AGB_AGE_CHOICES, GENDER_CHOICES, NOVICE_CHOICES, Bowstyle,
)
from entries.models import CompetitionEntry, Session, SessionRound

MATCH_TYPES = (
    ('T', 'Sets (old placing rules)'),
    ('U', 'Sets'),
    ('C', 'Score'),
)


TEAM_TYPES = (
    ('', 'Individual'),
    ('T', 'Team'),
    ('X', 'Mixed team'),
)


class OlympicRound(models.Model):
    distance = models.PositiveIntegerField()
    match_type = models.CharField(max_length=1, choices=MATCH_TYPES)
    team_type = models.CharField(max_length=1, blank=True, default='', choices=TEAM_TYPES)

    @property
    def arrows_per_end(self):
        if self.team_type == 'T':
            return 6
        elif self.team_type == 'X':
            return 4
        return 3

    @property
    def ends(self):
        if self.team_type:
            return 4
        return 5

    def short_name(self):
        return '{}m ({})'.format(self.distance, self.get_match_type_display())

    def __str__(self):
        return '{} Olympic Round at {}m ({})'.format(self.get_team_type_display(), self.distance, self.get_match_type_display())


class Category(models.Model):
    bowstyles = models.ManyToManyField(Bowstyle)
    ages = ArrayField(models.CharField(max_length=4, choices=AGB_AGE_CHOICES), blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    novice = models.CharField(max_length=1, choices=NOVICE_CHOICES, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return u'Category: {0}'.format(self.name)

    @property
    def code(self):
        code = ''
        if self.novice:
            code += self.novice
        code += ''.join([str(b)[0] for b in self.bowstyles.order_by()])
        if self.ages:
            code += ''.join(self.ages)
        if self.gender:
            code += self.get_gender_display()[0]
        return code

    @property
    def name(self):
        name = ''
        if self.novice:
            name += self.get_novice_display() + ' '
        name += u', '.join([str(b) for b in self.bowstyles.order_by('id')]) + ' '
        if self.ages:
            name += ', '.join([dict(AGB_AGE_CHOICES)[age] for age in self.ages]) + ' '
        if self.gender:
            name += self.get_gender_display() + ' '
        return name.strip()


class OlympicSessionRound(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    shot_round = models.ForeignKey(OlympicRound, on_delete=models.CASCADE)
    ranking_rounds = models.ManyToManyField(SessionRound)
    exclude_ranking_rounds = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    cut = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return u'{0}, {1} {2}'.format(self.session, self.shot_round, self.category.name)

    @cached_property
    def scoring_type(self):
        return self.ranking_rounds.all()[0].scoring_type

    def set_seedings(self, scores):
        for i, score in enumerate(scores):
            if score.is_team:
                entry, entry_2, entry_3 = None, None, None
                entry = score.team[0].target.session_entry.competition_entry
                entry_2 = score.team[1].target.session_entry.competition_entry
                if len(score.team) > 2:
                    entry_3 = score.team[2].target.session_entry.competition_entry
                self.seeding_set.create(
                    entry=entry,
                    entry_2=entry_2,
                    entry_3=entry_3,
                    seed=i + 1,
                )
            else:
                self.seeding_set.create(
                    entry=score.target.session_entry.competition_entry,
                    seed=i + 1,
                )

    def _get_match_layout(self, level, half_only=False, quarter_only=False, eighth_only=False, three_quarters=False):
        seedings = [1, 2]
        for m in range(2, level):
            n_arch = Match.objects.n_archers_for_level(m)
            seedings = map(lambda x: [x, n_arch + 1 - x] if x % 2 else [n_arch + 1 - x, x], seedings)
            seedings = [item for sublist in seedings for item in sublist]
        if half_only:
            seedings = [item for item in seedings if item > 2 ** (level - 2)]
        elif quarter_only:
            seedings = [item for item in seedings if item > 2 ** (level - 2) + 2 ** (level - 3)]
        elif eighth_only:
            seedings = [item for item in seedings if item > 2 ** (level - 2) + 2 ** (level - 3) + 2 ** (level - 4)]
        elif three_quarters:
            seedings = [item for item in seedings if item > 2 ** (level - 2) - 2 ** (level - 3)]
        return seedings

    def _get_target_mapping(self, level, start=1, expanded=False, half_only=False, quarter_only=False, eighth_only=False, three_quarters=False, offset=0):
        layout = self._get_match_layout(level, half_only, quarter_only, eighth_only, three_quarters)
        return [(m + offset, layout.index(m) * (1 + int(expanded)) + start) for m in layout]

    def make_matches(
            self, level, start=1, expanded=False, half_only=False,
            quarter_only=False, eighth_only=False, three_quarters=False,
            first_half_only=False, second_half_only=False, full_ranked=False,
            timing=None):
        if not first_half_only and not second_half_only:
            self.remove_matches(level)
        mapping = self._get_target_mapping(level, start, expanded, half_only, quarter_only, eighth_only, three_quarters)
        if full_ranked:
            # TODO: This is not really full_ranked yet, it's just "5th-8th"
            mapping += self._get_target_mapping(level, start + 2, expanded, offset=2)
        size = len(mapping)
        if first_half_only:
            mapping = mapping[:int(size / 2)]
        elif second_half_only:
            offset = size if expanded else size / 2
            mapping = [(match_id, target - offset) for match_id, target in mapping[int(size / 2):size]]
        for match_id, target in mapping:
            match = Match(
                session_round=self,
                target=target,
                level=level,
                match=match_id,
                timing=timing,
            )
            if expanded:
                match.target_2 = match.target + 1
            match.save()

    def remove_matches(self, level):
        self.match_set.filter(level=level).delete()

    def pretty_rank(self, rank, extra_rank_info=None):
        if rank <= 8:
            if extra_rank_info:
                index = rank - 5
                last_result = list(extra_rank_info[index][1])[0]
                if last_result.match.session_round.shot_round.match_type == 'T':
                    while index > 0 and last_result.total == list(extra_rank_info[index - 1][1])[0].total:
                        if last_result.arrow_total == list(extra_rank_info[index - 1][1])[0].arrow_total:
                            index -= 1
                        else:
                            # TODO: This doesn't work but it would be nice if it did
                            last_result.total = '%s (%s)' % (last_result.total, last_result.arrow_total)
                    rank = index + 5
                if last_result.match.session_round.shot_round.match_type == 'C':
                    while index > 0 and last_result.total == list(extra_rank_info[index - 1][1])[0].total:
                        index -= 1
                    rank = index + 5
            return rank
        real_rank = 8
        while real_rank < rank:
            real_rank = real_rank * 2
        return int(real_rank / 2) + 1

    def get_results(self):

        class OlympicResults(object):
            def __init__(self, results, total_levels):
                self.results = results
                self.total_levels = total_levels

        seedings = self.seeding_set.all().select_related().prefetch_related('result_set')
        total_levels = self.match_set.aggregate(models.Max('level'))['level__max']

        seedings_with_results = []
        for seeding in seedings:
            results = seeding.result_set.order_by('match__level')
            seedings_with_results.append((seeding, results))

        seedings_with_results = sorted(
            seedings_with_results,
            key=lambda s: (
                s[1][0].match.level,
                s[1][0].match.match if s[1][0].match.level == 1 else None,
                -s[1][0].total,
                -s[1][0].arrow_total,
                -s[1][0].win,
                s[0].seed,
            )
        )

        full_results = []
        for rank, (seeding, results) in enumerate(seedings_with_results):
            rank = rank + 1
            extra_rank_info = None
            if rank in [6, 7, 8]:
                extra_rank_info = seedings_with_results[4:8]
            rank = self.pretty_rank(rank, extra_rank_info)
            seeding.results = results
            seeding.rank = rank
            full_results.append(seeding)

        return OlympicResults(full_results, total_levels)


class Seeding(models.Model):
    entry = models.ForeignKey(CompetitionEntry, on_delete=models.CASCADE)
    entry_2 = models.ForeignKey(CompetitionEntry, blank=True, null=True, related_name='+', on_delete=models.CASCADE)
    entry_3 = models.ForeignKey(CompetitionEntry, blank=True, null=True, related_name='+', on_delete=models.CASCADE)
    session_round = models.ForeignKey(OlympicSessionRound, on_delete=models.CASCADE)
    seed = models.PositiveIntegerField()

    def __str__(self):
        return u'Seed {0} - {1} {2}'.format(self.seed, self.session_round.shot_round, self.entry)

    def label(self):
        if self.entry_2_id:
            return self.entry.team_name()
        return str(self.entry.archer)


class MatchManager(models.Manager):

    def n_matches_for_level(self, level):
        return 2 ** (level - 1)

    def n_archers_for_level(self, level):
        return self.n_matches_for_level(level) * 2

    def match_number_for_seed(self, seed, level):
        if level == 1:
            return 1

        # get to the first level archer would have their "seed" match
        n = 1
        while self.n_archers_for_level(n) < seed:
            n += 1

        # if we are still at a lower level than the current one, then the
        # archer will be in the same seed as their match
        # move seed down til we get to level
        if n < level:
            return seed

        # step down "knocking out" each seed
        while seed > self.n_matches_for_level(level):
            if seed > self.n_archers_for_level(n) - seed + 1:
                seed = self.n_archers_for_level(n) - seed + 1
            n -= 1
        return seed

    def effective_seed(self, seed, level):
        return self.match_number_for_seed(seed, level + 1)

    def match_for_seed(self, seed, level):
        match_number = self.match_number_for_seed(seed.seed, level)
        match = self.get(level=level, session_round=seed.session_round, match=match_number)
        return match

    def target_for_seed(self, seed, level):
        try:
            match = self.match_for_seed(seed, level)
        except self.model.DoesNotExist:
            return None
        effective_seed = self.effective_seed(seed.seed, level)
        if match.target_2 and effective_seed > self.n_matches_for_level(level):
            return (match.target_2, match.timing)
        return (match.target, match.timing)

    def matches_for_seed(self, seed, highest_seed=None):
        highest_level = self.filter(session_round=seed.session_round).order_by('-level')[:1]
        if not highest_level.exists():
            return None
        highest_level = highest_level[0].level
        matches = []
        for level in range(1, highest_level + 1):
            if highest_seed and self.n_archers_for_level(level) + 1 - seed.seed > highest_seed:
                matches.append((None, None))
            else:
                matches.append(self.target_for_seed(seed, level))
        return matches


class Match(models.Model):
    session_round = models.ForeignKey(OlympicSessionRound, on_delete=models.CASCADE)
    target = models.PositiveIntegerField()
    # for later matches spread across 2 bosses
    target_2 = models.PositiveIntegerField(blank=True, null=True)
    level = models.PositiveIntegerField()
    match = models.PositiveIntegerField()
    timing = models.PositiveIntegerField(null=True)

    objects = MatchManager()

    class Meta:
        verbose_name_plural = 'matches'

    def __str__(self):
        return u'Match {0} at level {1} on round {2}'.format(self.match, self.level, self.session_round)

    @property
    def match_name(self):
        """Name for this specific match, respecting for_placing"""
        if self.level == 1:
            return self.round_name
        return '%s Match %s' % (self.round_name, self.effective_match)

    @property
    def round_name(self):
        """Name for the round, respecting "for_placing"."""
        levels = ['Final', 'Semis', 'Quarters', '1/8', '1/16', '1/32', '1/64', '1/128', '1/256']
        for_placing = self.for_placing
        if for_placing == 1:
            return levels[self.level - 1]
        if for_placing == 3:
            return 'Bronze'
        return '%sth %s' % (for_placing, levels[self.level - 1])

    @property
    def n_archers_this_round(self):
        return Match.objects.n_archers_for_level(self.level)

    @property
    def n_matches_this_round(self):
        return Match.objects.n_matches_for_level(self.level)

    @property
    def n_archers_next_round(self):
        if self.level == 1:
            return None
        return Match.objects.n_archers_for_level(self.level - 1)

    @property
    def n_matches_next_round(self):
        if self.level == 1:
            return None
        return Match.objects.n_matches_for_level(self.level - 1)

    @property
    def for_placing(self):
        round_size = self.n_matches_this_round
        counter = 0
        while self.match > (counter + 1) * round_size:
            counter += 1
        return 1 + counter * round_size * 2

    @property
    def effective_match(self):
        round_size = self.n_matches_this_round
        effective_match = self.match
        while effective_match > round_size:
            effective_match -= round_size
        return effective_match

    def get_next_match_number(self, win=True):
        next_number = math.ceil(self.effective_match / 2)
        if win:
            return (self.for_placing - 1) / 2 + next_number
        return (self.for_placing + self.n_archers_next_round - 1) / 2 + next_number

    def update_totals(self):
        results = self.result_set.all()
        if not len(results) == 2:
            return
        result_1, result_2 = results
        result_1.total = result_2.total = 0
        result_1.win = result_2.win = False

        if result_1.dns:
            result_2.win = True
            result_2.win_by_forfeit = True
            result_1.save()
            result_2.save()
            return
        elif result_2.dns:
            result_1.win = True
            result_1.win_by_forfeit = True
            result_1.save()
            result_2.save()
            return

        arrows_1 = result_1.matcharrow_set.order_by('arrow_of_round')
        arrows_2 = result_2.matcharrow_set.order_by('arrow_of_round')
        if self.session_round.shot_round.match_type == 'C':
            result_1.total = sum(arrows_1[:15], key=lambda a: a.arrow_value)
            result_2.total = sum(arrows_2[:15], key=lambda a: a.arrow_value)
            if result_1.total > result_2.total and len(arrows_1) >= 15 and len(arrows_2) >= 15:
                result_1.win = True
                result_2.win = False
            if result_1.total < result_2.total and len(arrows_1) >= 15 and len(arrows_2) >= 15:
                result_2.win = True
                result_1.win = False
            else:
                so_1 = next(filter(lambda a: a.arrow_of_round == 16, arrows_1), None)
                so_2 = next(filter(lambda a: a.arrow_of_round == 16, arrows_2), None)
                if so_1 and so_2:
                    if so_1.arrow_value > so_2.arrow_value or (so_1.arrow_value == so_2.arrow_value and so_1.closest and not so_2.closest):
                        result_1.win = True
                        result_2.win = False
                    elif so_1.arrow_value < so_2.arrow_value or (so_1.arrow_value == so_2.arrow_value and not so_1.closest and so_2.closest):
                        result_2.win = True
                        result_1.win = False
        elif self.session_round.shot_round.match_type == 'U':
            for i in range(5):
                pts_1, pts_2 = self.set_result(arrows_1, arrows_2, i)
                result_1.total += pts_1
                result_2.total += pts_2
            if result_1.total >= 6:
                result_1.win = True
                result_2.win = False
            elif result_2.total >= 6:
                result_2.win = True
                result_1.win = False
            else:
                so_1 = next(filter(lambda a: a.arrow_of_round == 16, arrows_1), None)
                so_2 = next(filter(lambda a: a.arrow_of_round == 16, arrows_2), None)
                if so_1 and so_2:
                    if so_1.arrow_value > so_2.arrow_value or (so_1.arrow_value == so_2.arrow_value and so_1.closest and not so_2.closest):
                        result_1.total = 6
                        result_1.win = True
                        result_2.win = False
                    elif so_1.arrow_value < so_2.arrow_value or (so_1.arrow_value == so_2.arrow_value and not so_1.closest and so_2.closest):
                        result_2.total = 6
                        result_2.win = True
                        result_1.win = False

        result_1.save()
        result_2.save()

    def set_result(self, arrows_1, arrows_2, set_number):
        def filter_fn(a):
            return a.arrow_of_round in range(3 * set_number + 1, 3 * set_number + 4)

        if not list(filter(filter_fn, arrows_1)):
            return 0, 0
        if not list(filter(filter_fn, arrows_2)):
            return 0, 0

        score_1 = sum(map(lambda a: a.arrow_value, filter(filter_fn, arrows_1)))
        score_2 = sum(map(lambda a: a.arrow_value, filter(filter_fn, arrows_2)))
        if score_1 > score_2:
            return 2, 0
        elif score_1 < score_2:
            return 0, 2
        return 1, 1


class Result(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    seed = models.ForeignKey(Seeding, on_delete=models.CASCADE)

    total = models.PositiveIntegerField()
    arrow_total = models.PositiveIntegerField(default=0)
    win = models.BooleanField(default=False)
    dns = models.BooleanField(default=False)
    win_by_forfeit = models.BooleanField(default=False)

    def __str__(self):
        return u'Result of match {0}'.format(self.match)

    def display(self):
        if self.dns:
            return 'DNS'
        if self.win_by_forfeit:
            return 'BYE'
        return self.total


class MatchArrow(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    arrow_value = models.PositiveIntegerField()
    arrow_of_round = models.PositiveIntegerField()
    is_x = models.BooleanField(default=False)
    closest = models.BooleanField(default=False)

    class Meta:
        unique_together = [('arrow_of_round', 'result')]

    def __str__(self):
        if self.is_x:
            return 'X'
        if self.arrow_value == 0:
            return 'M'
        return str(self.arrow_value)
