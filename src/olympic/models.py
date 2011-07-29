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
        return 'Olympic Round at {0}m'.format(self.distance)

class Category(models.Model):
    bowstyles = models.ManyToMany(Bowstyle)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    def __unicode__(self):
        return u'Category: {0} '.format(self.get_gender_display()) + ', '.join(self.bowstyles.all())

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
    target = models.PostitiveIntegerField()
    level = models.PositiveIntegerField()
    match = models.PostitiveIntegerField()

    def __unicode__(self):
        return u'Match {0} at level {1}'.format(self.match, self.level)

class Result(models.Model):
    match = models.ForeignKey(Match)
    winner = models.ForeignKey(Seeding)
    loser = models.ForeignKey(Seeding)
