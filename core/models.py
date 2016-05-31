import json

from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify

from custom_user.models import AbstractEmailUser


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

WA_AGE_CHOICES = (
    ('C', 'Cadet'),
    ('J', 'Junior'),
    ('', 'Senior'),  # Map senior to '' as we never really print it
    ('M', 'Master'),
)

AGB_AGE_CHOICES = (
    ('', 'Senior'),
    ('U18', 'U18'),
    ('U16', 'U16'),
    ('U14', 'U14'),
    ('U12', 'U12'),
)


class User(AbstractEmailUser):
    name = models.CharField(max_length=255, default='')

    def __str__(self):
        return self.name


class Subround(models.Model):
    arrows = models.PositiveIntegerField()
    distance = models.PositiveIntegerField()
    unit = models.CharField(max_length=1, choices=DISTANCE_UNITS)
    target_face = models.PositiveIntegerField()

    def __str__(self):
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

    def __str__(self):
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
        if self.scoring_type == 'X':
            return ['10+X', 'X']
        elif self.scoring_type == 'I':
            return ['10s']
        else:
            return ['H', 'G']

    @property
    def scoring_headings(self):
        if self.scoring_type == 'X':
            return ['10s+Xs', 'Xs']
        elif self.scoring_type == 'I':
            return ['10s']
        else:
            return ['Hits', 'Golds']


class Bowstyle(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = 'countries'

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=50, unique=True)
    country = models.ForeignKey(Country)

    def __str__(self):
        return self.name


class County(models.Model):
    name = models.CharField(max_length=500, unique=True)
    short_name = models.CharField(max_length=50, unique=True)
    region = models.ForeignKey(Region)

    class Meta:
        verbose_name_plural = 'counties'
        ordering = ('short_name',)

    def __str__(self):
        return self.short_name


class Club(models.Model):
    name = models.CharField(max_length=500, unique=True)
    short_name = models.CharField(max_length=50, unique=True)

    county = models.ForeignKey(County, blank=True, null=True)

    slug = models.SlugField(editable=False, unique=True)

    class Meta:
        ordering = ('short_name',)

    def clean(self, *args, **kwargs):
        self.slug = slugify(self.short_name)
        return super(Club, self).clean(*args, **kwargs)

    def __str__(self):
        return self.short_name

    def json(self):
        return json.dumps({
            'id': self.pk,
            'name': self.name,
            'short_name': self.short_name,
        })

    def get_absolute_url(self):
        return reverse('club_detail', kwargs={'club_slug': self.slug})


class Archer(models.Model):
    name = models.CharField(max_length=200)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    club = models.ForeignKey(Club, blank=True, null=True)
    bowstyle = models.ForeignKey(Bowstyle)
    age = models.CharField(max_length=1, choices=AGE_CHOICES, default='S')
    wa_age = models.CharField(max_length=1, choices=WA_AGE_CHOICES, default='', blank=True)
    agb_age = models.CharField(max_length=3, choices=AGB_AGE_CHOICES, default='', blank=True)
    novice = models.CharField(max_length=1, choices=NOVICE_CHOICES, default='E')
    agb_number = models.BigIntegerField(blank=True, null=True)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def json(self):
        return json.dumps({
            'id': self.pk,
            'name': self.name,
            'age': self.age,
            'wa_age': self.wa_age,
            'agb_age': self.agb_age,
            'gender': self.gender,
            'club': self.club.pk,
            'bowstyle': self.bowstyle.pk,
            'novice': self.novice,
            'agb_number': self.agb_number,
        })

    def merge_into(self, other):
        self.competitionentry_set.update(archer=other)
        self.delete()
