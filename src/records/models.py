from django.db import models

from itertools import groupby
import json

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)

class Competition(models.Model):
    date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def clean(self, *args, **kwargs):
        if self.end_date is None:
            self.end_date = self.date
        return super(Competition, self).clean(*args, **kwargs)

    def full_results(self):
        ordering = ['bowstyle', 'archer__gender', '-score', '-hits', '-golds']
        all_scores = self.entry_set.select_related().order_by(*ordering)
        results = []
        for key, group in groupby(all_scores, lambda s: s.get_classification()):
            results.append({
                'class': key,
                'scores': list(group)
            })
        return results

    def __unicode__(self):
        return 'OUIT: {0}'.format(self.date.year)

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
    competition = models.ForeignKey(Competition)
    archer = models.ForeignKey(Archer)
    club = models.ForeignKey(Club)
    bowstyle = models.ForeignKey(Bowstyle)

    score = models.IntegerField(blank=True, null=True)
    hits = models.IntegerField(blank=True, null=True)
    golds = models.IntegerField(blank=True, null=True)

    def clean(self, *args, **kwargs):
        if self.club is None:
            self.club = self.archer.club
        if self.bowstyle is None:
            self.bowstyle = self.archer.bowstyle
        return super(Entry, self).clean(*args, **kwargs)

    def get_classification(self):
        return '{0} {1}'.format(self.bowstyle, self.archer.get_gender_display())

    def __unicode__(self):
        return '{0} at {1}'.format(self.archer, self.competition)

