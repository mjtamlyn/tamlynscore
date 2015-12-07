from django.db import models


class League(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Season(models.Model):
    name = models.CharField(max_length=255)
    league = models.ForeignKey('League')
    clubs = models.ManyToManyField('core.Club')

    def __unicode__(self):
        return self.name


class Leg(models.Model):
    season = models.ForeignKey('Season')
    competitions = models.ManyToManyField('entries.Competition')
    clubs = models.ManyToManyField('core.Club')
    index = models.PositiveIntegerField()

    def __unicode__(self):
        return '%s Leg %s' (self.season, self.index)
