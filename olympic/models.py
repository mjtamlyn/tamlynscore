from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.functional import cached_property

from core.models import (
    GENDER_CHOICES, JUNIOR_MASTERS_AGE_CHOICES, NOVICE_CHOICES, WA_AGE_CHOICES,
    Bowstyle,
)
from entries.models import CompetitionEntry, Session, SessionRound

MATCH_TYPES = (
    ('T', 'Sets'),
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
    wa_ages = ArrayField(models.CharField(max_length=1, choices=WA_AGE_CHOICES), blank=True, null=True)
    junior_masters_age = models.CharField(max_length=3, choices=JUNIOR_MASTERS_AGE_CHOICES, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    novice = models.CharField(max_length=1, choices=NOVICE_CHOICES, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return u'Category: {0}'.format(self.name)

    def code(self):
        code = ''
        if self.wa_ages:
            code += ''.join(self.wa_ages)
        if self.junior_masters_age:
            code += ''.join(self.junior_masters_age)
        if self.novice:
            code += self.novice
        if self.gender:
            code += self.gender
        return code + u''.join([str(b)[0] for b in self.bowstyles.all()])

    def short_code(self):
        code = ''
        if self.wa_ages:
            code += ''.join(self.wa_ages)
        if self.novice:
            code += self.novice
        if self.gender:
            code += self.gender
        return code + str(self.bowstyles.all()[0])[0]

    @property
    def name(self):
        name = ''
        if self.wa_ages:
            name += ', '.join([dict(WA_AGE_CHOICES)[age] for age in self.wa_ages]) + ' '
        if self.junior_masters_age:
            name += self.get_junior_masters_age_display() + ' '
        if self.novice:
            name += self.get_novice_display() + ' '
        if self.gender:
            name += self.get_gender_display() + ' '
        return name + u', '.join([str(b) for b in self.bowstyles.all()])

    @property
    def short_name(self):
        name = ''
        if self.wa_ages:
            name += ', '.join([dict(WA_AGE_CHOICES)[age] for age in self.wa_age_choices]) + ' '
        if self.junior_masters_age:
            name += self.get_junior_masters_age_display() + ' '
        if self.novice:
            name += self.get_novice_display() + ' '
        if self.gender:
            name += self.get_gender_display() + ' '
        return name + str(self.bowstyles.all()[0])


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
        return self.ranking_rounds.all()[0].shot_round.scoring_type

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
            seedings = map(lambda x: [x, 2 ** m + 1 - x] if x % 2 else [2 ** m + 1 - x, x], seedings)
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

    def _get_target_mapping(self, level, start=1, expanded=False, half_only=False, quarter_only=False, eighth_only=False, three_quarters=False):
        layout = self._get_match_layout(level, half_only, quarter_only, eighth_only, three_quarters)
        return [(m, layout.index(m) * (1 + int(expanded)) + start) for m in layout]

    def make_matches(self, level, start=1, expanded=False, half_only=False, quarter_only=False, eighth_only=False, three_quarters=False, first_half_only=False, second_half_only=False, timing=None):
        if not first_half_only and not second_half_only:
            self.remove_matches(level)
        mapping = self._get_target_mapping(level, start, expanded, half_only, quarter_only, eighth_only, three_quarters)
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

    def _match_number_for_seed(self, seed, level):
        if level == 1:
            return 1
        # get supremum
        n = 1
        while 2 ** n < seed:
            n += 1
        # move seed down til we get to level
        while n >= level and seed > 2 ** (level - 1):
            if seed <= 2 ** (n - 1):
                n -= 1
                continue
            seed = 2 ** n - seed + 1
            n -= 1
        return seed

    def _effective_seed(self, seed, level):
        return self._match_number_for_seed(seed, level + 1)

    def match_for_seed(self, seed, level):
        match_number = self._match_number_for_seed(seed.seed, level)
        match = self.get(level=level, session_round=seed.session_round, match=match_number)
        return match

    def target_for_seed(self, seed, level):
        try:
            match = self.match_for_seed(seed, level)
        except self.model.DoesNotExist:
            return None
        effective_seed = self._effective_seed(seed.seed, level)
        if match.target_2 and effective_seed * 2 > 2 ** level:
            return (match.target_2, match.timing)
        return (match.target, match.timing)

    def matches_for_seed(self, seed, highest_seed=None):
        highest_level = self.filter(session_round=seed.session_round).order_by('-level')[:1]
        if not highest_level.exists():
            return None
        highest_level = highest_level[0].level
        matches = []
        for level in range(1, highest_level + 1):
            if highest_seed and 2 ** level + 1 - seed.seed > highest_seed:
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
