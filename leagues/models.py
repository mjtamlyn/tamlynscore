from django.db import models
from django.urls import reverse

from entries.models import ResultsFormatFields
from scores.result_modes import get_result_modes


class League(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)

    def get_absolute_url(self):
        return reverse('league-detail', kwargs={'league_slug': self.slug})

    def get_current_season(self):
        return self.season_set.order_by('start_date').last()


class Season(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    league = models.ForeignKey('League', on_delete=models.CASCADE)
    non_leg_competitions = models.ManyToManyField('entries.Competition')
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-start_date',)

    def get_absolute_url(self):
        return reverse('season-detail', kwargs={'league_slug': self.league.slug, 'season_slug': self.slug})


class Leg(ResultsFormatFields, models.Model):
    season = models.ForeignKey('Season', on_delete=models.CASCADE)
    competitions = models.ManyToManyField('entries.Competition')
    index = models.PositiveIntegerField()

    def __str__(self):
        return '%s Leg %s' % (self.season, self.index)


class ResultsMode(models.Model):
    leg = models.ForeignKey('Leg', related_name='result_modes', on_delete=models.CASCADE)
    mode = models.CharField(max_length=31, choices=tuple(get_result_modes()))

    class Meta:
        unique_together = ('leg', 'mode')

    def __str__(self):
        return str(self.get_mode_display())

    def get_absolute_url(self):
        return reverse('leg-results', kwargs={
            'mode': self.mode,
            'format': 'html',
            'leg_index': self.leg.index,
            'season_slug': self.leg.season.slug,
            'league_slug': self.leg.season.league.slug,
        })
