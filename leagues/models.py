from django.core.urlresolvers import reverse
from django.db import models


class League(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)

    def get_absolute_url(self):
        return reverse('league-detail', kwargs={'league_slug': self.slug})


class Season(models.Model):
    name = models.CharField(max_length=255)
    league = models.ForeignKey('League')
    clubs = models.ManyToManyField('core.Club')
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name


class Leg(models.Model):
    season = models.ForeignKey('Season')
    competitions = models.ManyToManyField('entries.Competition')
    clubs = models.ManyToManyField('core.Club')
    index = models.PositiveIntegerField()

    def __str__(self):
        return '%s Leg %s' (self.season, self.index)
