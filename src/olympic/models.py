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

    def __unicode__(self):
        return 'Olympic Round at {0}m ({1})'.format(self.distance, self.get_match_type_display())

class Category(models.Model):
    bowstyles = models.ManyToManyField(Bowstyle)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    class Meta:
        verbose_name_plural = 'categories'

    def __unicode__(self):
        return u'Category: {0} '.format(self.get_gender_display()) + u', '.join([unicode(b) for b in self.bowstyles.all()])

    def code(self):
        return self.gender + u''.join([unicode(b)[0] for b in self.bowstyles.all()])

class OlympicSessionRound(models.Model):
    session = models.ForeignKey(Session)
    shot_round = models.ForeignKey(OlympicRound)
    ranking_round = models.ForeignKey(SessionRound)
    category = models.ForeignKey(Category)

    def __unicode__(self):
        return u'{0}, {1}'.format(self.session, self.shot_round)

    def set_seedings(self, scores):
        scores = Score.objects.results(self.ranking_round, leaderboard=False, category=self.category).filter(pk__in=scores)
        for score in scores:
            seeding = Seeding(
                    entry=score.target.session_entry.competition_entry,
                    session_round=self,
                    seed=list(scores).index(score) + 1,
            )
            seeding.save()

    def _get_match_layout(self, level, half_only=False):
        seedings = [1, 2]
        for m in range(2, level):
            seedings = map(lambda x: [x, 2 ** m + 1 - x] if x % 2 else [2 ** m + 1 - x, x], seedings)
            seedings = [item for sublist in seedings for item in sublist]
        if half_only:
            seedings = [item for item in seedings if item > 2 ** (level - 2)]
        return seedings

    def _get_target_mapping(self, level, start=1, expanded=False, half_only=False):
        layout = self._get_match_layout(level, half_only)
        return [(m, layout.index(m) * (1 + int(expanded)) + start) for m in layout]

    def make_matches(self, level, start=1, expanded=False, half_only=False):
        mapping = self._get_target_mapping(level, start, expanded, half_only)
        for match_id, target in mapping:
            match = Match(
                    session_round=self,
                    target=target,
                    level=level,
                    match=match_id,
            )
            if expanded:
                match.target_2 = match.target + 1
            match.save()

class Seeding(models.Model):
    entry = models.ForeignKey(CompetitionEntry)
    session_round = models.ForeignKey(OlympicSessionRound)
    seed = models.PositiveIntegerField()

    def __unicode__(self):
        return u'Seed {0} - {1} {2}'.format(self.seed, self.session_round.shot_round, self.entry)

class MatchManager(models.Manager):

    def _match_number_for_seed(self, seed, level):
        # get supremum
        n = 1
        while 2 ** n < seed:
            n += 1
        # move seed down til we get to level
        while n > level and seed > 2 ** level:
            if seed < 2 ** (n - 1):
                n -= 1
                continue
            seed = 2 ** n - seed + 1
            n -= 1
        return seed

    def target_for_seed(self, seed, level):
        match_number = self._match_number_for_seed(seed.seed, level)
        match = self.get(level=level, session_round=seed.session_round, match=match_number)
        if match.target_2 and seeding.seed * 2 < level:
            return match.target_2
        return match.target

class Match(models.Model):
    session_round = models.ForeignKey(OlympicSessionRound)
    target = models.PositiveIntegerField()
    # for later matches spread across 2 bosses
    target_2 = models.PositiveIntegerField(blank=True, null=True)
    level = models.PositiveIntegerField()
    match = models.PositiveIntegerField()

    objects = MatchManager()

    class Meta:
        verbose_name_plural = 'matches'

    def __unicode__(self):
        return u'Match {0} at level {1} on round {2}'.format(self.match, self.level, self.session_round)

class Result(models.Model):
    match = models.ForeignKey(Match)
    winner = models.ForeignKey(Seeding, related_name='result_winner_set')
    loser = models.ForeignKey(Seeding, null=True, blank=True, related_name='result_loser_set')

    def __unicode__(self):
        return u'Result of match {0}'.format(self.match)
