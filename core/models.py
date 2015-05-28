import json

from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify


DISTANCE_UNITS = (
    ('m', 'metres'),
    ('y', 'yards'),
)


SCORING_TYPES = (
    ('F', 'Five Zone Imperial'),
    ('T', 'AGB Indoor - Ten Zone, no Xs, with hits'),
    ('X', 'WA Outdoor - Ten Zone, with Xs, no hits'),
    ('I', 'WA Indoor - Ten Zone, no Xs, no hits'),
    ('W', 'Worcester'),
)


GENDER_CHOICES = (
    ('G', 'Gent'),
    ('L', 'Lady'),
)


NOVICE_CHOICES = (
    ('N', 'Novice'),
    ('E', 'Experienced'),
)


AGE_CHOICES = (
    ('J', 'Junior'),
    ('S', 'Senior'),
)


class Subround(models.Model):
    arrows = models.PositiveIntegerField()
    distance = models.PositiveIntegerField()
    unit = models.CharField(max_length=1, choices=DISTANCE_UNITS)
    target_face = models.PositiveIntegerField()

    def __unicode__(self):
        return u'{0} arrows at {1} {2} ({3}cm)'.format(
            self.arrows,
            self.distance,
            self.get_unit_display(),
            self.target_face,
        )

    class Meta:
        ordering = ('unit', '-distance', '-arrows', '-target_face')


class Round(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subrounds = models.ManyToManyField(Subround)
    scoring_type = models.CharField(max_length=1, choices=SCORING_TYPES)

    def __unicode__(self):
        return self.name

    @property
    def arrows(self):
        return self.subrounds.aggregate(models.Sum('arrows'))['arrows__sum']

    def get_subround(self, doz_no):
        arrows = int(doz_no) * 12
        subrounds = self.subrounds.order_by('-distance')
        for subround in subrounds:
            if subround.arrows >= arrows:
                return subround
        raise Exception('There aren\'t that many dozens in that round!')

    @property
    def has_xs(self):
        return self.scoring_type == 'X'

    @property
    def score_sheet_headings(self):
        return ['10+X', 'X'] if self.has_xs else ['H', 'G']


class Bowstyle(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = 'countries'

    def __unicode__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=50, unique=True)
    country = models.ForeignKey(Country)

    def __unicode__(self):
        return self.name


class County(models.Model):
    name = models.CharField(max_length=50, unique=True)
    region = models.ForeignKey(Region)

    class Meta:
        verbose_name_plural = 'counties'

    def __unicode__(self):
        return self.name


class Club(models.Model):
    name = models.CharField(max_length=500, unique=True)
    short_name = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=10, blank=True, default='')

    county = models.ForeignKey(County, blank=True, null=True)

    slug = models.SlugField(editable=False, unique=True)

    class Meta:
        ordering = ('short_name',)

    def clean(self, *args, **kwargs):
        self.slug = slugify(self.short_name)
        return super(Club, self).clean(*args, **kwargs)

    def __unicode__(self):
        return self.short_name

    def json(self):
        return json.dumps({
            'id': self.pk,
            'name': self.name,
            'short_name': self.short_name,
        })

    def get_absolute_url(self):
        return reverse('club_detail', kwargs={'slug': self.slug})


class Archer(models.Model):
    name = models.CharField(max_length=200)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    club = models.ForeignKey(Club)
    bowstyle = models.ForeignKey(Bowstyle)
    age = models.CharField(max_length=1, choices=AGE_CHOICES, default='S')
    novice = models.CharField(max_length=1, choices=NOVICE_CHOICES, default='E')
    agb_number = models.BigIntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    def json(self):
        return json.dumps({
            'id': self.pk,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'club': self.club.pk,
            'bowstyle': self.bowstyle.pk,
            'novice': self.novice,
            'gnas_no': self.gnas_no,
        })
