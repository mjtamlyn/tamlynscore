from django.db import models

from core.models import Bowstyle, GENDER_CHOICES
from entries.models import Session, SessionRound, CompetitionEntry
from scores.models import Score


MATCH_TYPES = (
    ('T', 'Sets'),
    ('C', 'Score'),
)


class OlympicRound(models.Model):
    distance = models.PositiveIntegerField()
    match_type = models.CharField(max_length=1, choices=MATCH_TYPES)

    def __str__(self):
        return 'Olympic Round at {0}m ({1})'.format(self.distance, self.get_match_type_display())


class Category(models.Model):
    bowstyles = models.ManyToManyField(Bowstyle)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return u'Category: {0}'.format(self.name)

    def code(self):
        if self.gender:
            code = self.gender
        else:
            code = ''
        return code + u''.join([unicode(b)[0] for b in self.bowstyles.all()])

    def short_code(self):
        if self.gender:
            code = self.gender
        else:
            code = ''
        return code + unicode(self.bowstyles.all()[0])[0]

    @property
    def name(self):
        if self.gender:
            name = self.get_gender_display() + ' '
        else:
            name = ''
        return name + u', '.join([unicode(b) for b in self.bowstyles.all()])

    @property
    def short_name(self):
        if self.gender:
            name = self.get_gender_display() + ' '
        else:
            name = ''
        return name + unicode(self.bowstyles.all()[0])


class OlympicSessionRound(models.Model):
    session = models.ForeignKey(Session)
    shot_round = models.ForeignKey(OlympicRound)
    ranking_round = models.ForeignKey(SessionRound)
    category = models.ForeignKey(Category)

    def __str__(self):
        return u'{0}, {1} {2}'.format(self.session, self.shot_round, self.category.name)

    def set_seedings(self, scores):
        scores = Score.objects.results(self.ranking_round, category=self.category).filter(pk__in=scores)
        scores = sorted(scores, key=lambda s: 0 - s.score)
        for score in scores:
            seeding = Seeding(
                    entry=score.target.session_entry.competition_entry,
                    session_round=self,
                    seed=list(scores).index(score) + 1,
            )
            seeding.save()

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

    def make_matches(self, level, start=1, expanded=False, half_only=False, quarter_only=False, eighth_only=False, three_quarters=False, timing=None):
        self.remove_matches(level)
        mapping = self._get_target_mapping(level, start, expanded, half_only, quarter_only, eighth_only, three_quarters)
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
        return real_rank/2 + 1

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

        seedings_with_results = sorted(seedings_with_results, key=lambda s: (s[1][0].match.level, s[1][0].match.match if s[1][0].match.level == 1 else None, -s[1][0].total, -s[1][0].arrow_total, -s[1][0].win, s[0].seed))

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
    entry = models.ForeignKey(CompetitionEntry)
    session_round = models.ForeignKey(OlympicSessionRound)
    seed = models.PositiveIntegerField()

    def __str__(self):
        return u'Seed {0} - {1} {2}'.format(self.seed, self.session_round.shot_round, self.entry)


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
    session_round = models.ForeignKey(OlympicSessionRound)
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
    match = models.ForeignKey(Match)
    seed = models.ForeignKey(Seeding)

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
