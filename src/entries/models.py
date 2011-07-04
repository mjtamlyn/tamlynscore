from django.db import models
from django.template.defaultfilters import slugify

from core.models import Archer, Bowstyle, Club, Round, AGE_CHOICES

SCORING_SYSTEMS = (
    ('F', 'Full running slips'),
    ('D', 'Dozen running slips'),
    ('T', 'Totals only'),
)

class Tournament(models.Model):
    full_name = models.CharField(max_length=300, unique=True)
    short_name = models.CharField(max_length=20)

    host_club = models.ForeignKey(Club)

    def __unicode__(self):
        return self.short_name

class Competition(models.Model):
    tournament = models.ForeignKey(Tournament)

    date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    slug = models.SlugField(editable=False, unique=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def clean(self, *args, **kwargs):
        if self.end_date is None:
            self.end_date = self.date
        self.slug = slugify('{0} {1}'.format(self.tournament, self.date.year))
        return super(Competition, self).clean(*args, **kwargs)

    def __unicode__(self):
        return u'{0}: {1}'.format(self.tournament, self.date.year)

    class Meta:
        unique_together = ('date', 'tournament')

class Session(models.Model):
    competition = models.ForeignKey(Competition)
    start = models.DateTimeField()

    scoring_system = models.CharField(max_length=1, choices=SCORING_SYSTEMS)

    def __unicode__(self):
        return u'{0} - {1}'.format(self.competition, self.start)

class SessionRound(models.Model):
    session = models.ForeignKey(Session)
    shot_round = models.ForeignKey(Round)

    def __unicode__(self):
        return u'{0}, {1}'.format(self.session, self.shot_round)

class CompetitionEntry(models.Model):
    competition = models.ForeignKey(Competition)

    archer = models.ForeignKey(Archer)
    club = models.ForeignKey(Club)
    bowstyle = models.ForeignKey(Bowstyle)
    age = models.CharField(max_length=1, choices=AGE_CHOICES)
    novice = models.BooleanField(default=False)

    def __unicode__(self):
        return u'{0} at {1}'.format(self.archer, self.competition)

    class Meta:
        verbose_name_plural = 'competition entries'

class SessionEntry(models.Model):
    competition_entry = models.ForeignKey(CompetitionEntry)
    session_round = models.ForeignKey(SessionRound)

    def __unicode__(self):
        return u'{0} - {1}'.format(self.competition_entry, self.session_round.shot_round)

    class Meta:
        verbose_name_plural = 'session entries'

class TargetAllocation(models.Model):
    session_entry = models.ForeignKey(SessionEntry)
    boss = models.PositiveIntegerField()
    target = models.CharField(max_length=1)

    def __unicode__(self):
        return u'{0}{1} - {2}'.format(self.boss, self.target, self.session_entry)
