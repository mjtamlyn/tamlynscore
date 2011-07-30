from django.db import models

from core.models import Bowstyle, GENDER_CHOICES
from entries.models import Session, SessionRound, CompetitionEntry

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

class Seeding(models.Model):
    entry = models.ForeignKey(CompetitionEntry)
    session_round = models.ForeignKey(OlympicSessionRound)
    seed = models.PositiveIntegerField()

    def __unicode__(self):
        return u'{0} - {1}'.format(self.competition_entry, self.session_round.shot_round)

class Match(models.Model):
    session_round = models.ForeignKey(OlympicSessionRound)
    target = models.PositiveIntegerField()
    level = models.PositiveIntegerField()
    match = models.PositiveIntegerField()

    class Meta:
        verbose_name_plural = 'matches'

    def __unicode__(self):
        return u'Match {0} at level {1}'.format(self.match, self.level)

class Result(models.Model):
    match = models.ForeignKey(Match)
    winner = models.ForeignKey(Seeding, related_name='result_winner_set')
    loser = models.ForeignKey(Seeding, null=True, blank=True, related_name='result_loser_set')

    def __unicode__(self):
        return u'Result of match {0}'.format(self.match)
