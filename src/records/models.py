from django.db import models

from itertools import groupby
import json

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)

DISTANCE_UNITS = (
    ('m', 'metres'),
    ('y', 'yards'),
)

class Tournament(models.Model):
    full_name = models.CharField(max_length=300)
    short_name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.short_name

class Subround(models.Model):
    arrows = models.PositiveIntegerField()
    distance = models.PositiveIntegerField()
    unit = models.CharField(max_length=1, choices=DISTANCE_UNITS)
    
    def __unicode__(self):
        return '{0} arrows at {1} {2}'.format(self.arrows, self.distance, self.get_unit_display())

class Round(models.Model):
    name = models.CharField(max_length=100)
    subrounds = models.ManyToManyField(Subround)

    def __unicode__(self):
        return self.name

class BoundRound(models.Model):
    round_type = models.ForeignKey(Round)
    competition = models.ForeignKey('Competition')

class Competition(models.Model):
    date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    rounds = models.ManyToManyField(Round, through=BoundRound)
    tournament = models.ForeignKey(Tournament)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def clean(self, *args, **kwargs):
        if self.end_date is None:
            self.end_date = self.date
        return super(Competition, self).clean(*args, **kwargs)

    def full_results(self):
        return []
        #TODO: fix this when we've got the db better laid out!
        #ordering = ['bowstyle', 'archer__gender', '-score', '-hits', '-golds']
        #all_scores = self.entry_set.select_related().order_by(*ordering)
        #results = []
        #for key, group in groupby(all_scores, lambda s: s.get_classification()):
        #    results.append({
        #        'class': key,
        #        'scores': list(group)
        #    })
        #return results

    def __unicode__(self):
        return '{0}: {1}'.format(self.tournament, self.date.year)

class Bowstyle(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Club(models.Model):
    name = models.CharField(max_length=500)
    short_name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.short_name

class Archer(models.Model):
    name = models.CharField(max_length=200)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    club = models.ForeignKey(Club)
    bowstyle = models.ForeignKey(Bowstyle)

    def __unicode__(self):
        return self.name

    def json(self):
        return json.dumps({
            'name': self.name,
            'gender': self.get_gender_display(),
            'club': self.club.pk,
            'bowstyle': self.bowstyle.pk,
        })

class Entry(models.Model):
    shot_round = models.ForeignKey(BoundRound)
    
    archer = models.ForeignKey(Archer)
    club = models.ForeignKey(Club)
    bowstyle = models.ForeignKey(Bowstyle)

    score = models.IntegerField(blank=True, null=True)
    hits = models.IntegerField(blank=True, null=True)
    golds = models.IntegerField(blank=True, null=True)

    def get_classification(self):
        return '{0} {1}'.format(self.bowstyle, self.archer.get_gender_display())

    def __unicode__(self):
        return '{0} at {1}'.format(self.archer, self.shot_round.competition)

    class Meta:
        verbose_name_plural = 'entries'

class Arrow(models.Model):
    subround = models.ForeignKey(Subround)
    entry = models.ForeignKey(Entry)
    score = models.PositiveIntegerField()
    arrow_of_round = models.PositiveIntegerField()

    def __unicode__(self):
        return unicode(self.score)
