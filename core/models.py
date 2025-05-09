import json

from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

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
    ('E', 'Xs are 11 - Eleven Zone, no hits'),
    ('W', 'Worcester'),
    ('S', 'Score only (e.g. IFAA Indoor)'),
)


GENDER_CHOICES = (
    ('G', 'Men'),
    ('L', 'Women'),
)


NOVICE_CHOICES = (
    ('N', 'Novice'),
    ('E', 'Experienced'),
)


SIMPLE_AGE_CHOICES = (
    ('J', 'Junior'),
    ('S', 'Senior'),
)

AGB_AGE_CHOICES = (
    ('', 'Senior'),
    ('50+', '50+'),
    ('65+', '65+'),
    ('U21', 'U21'),
    ('U18', 'U18'),
    ('U16', 'U16'),
    ('U15', 'U15'),
    ('U14', 'U14'),
    ('U12', 'U12'),
    ('U10', 'U10'),
)

IFAA_DIVISIONS = (
    ('P', 'Professional'),
    ('C', 'Cub'),
    ('J', 'Junior'),
    ('YA', 'Young Adult'),
    ('A', 'Adult'),
    ('V', 'Veteran'),
    ('S', 'Senior'),
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
        return '{0} arrows at {1} {2} ({3}cm)'.format(
            self.arrows,
            self.distance,
            self.get_unit_display(),
            self.target_face,
        )

    @property
    def distance_short(self):
        return '{}{}'.format(self.distance, self.unit)

    class Meta:
        ordering = ('unit', '-distance', '-arrows', '-target_face')


class Round(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subrounds = models.ManyToManyField(Subround)
    longest_distance = models.IntegerField(default=0)  # Used for ordering results
    scoring_type = models.CharField(max_length=1, choices=SCORING_TYPES)
    can_split = models.BooleanField(
        default=False, help_text=(
            'If the round does not have multiple subrounds, but it makes sense '
            'to talk about two halves of the round (e.g. a WA18m or WA70m), then '
            'tick this box and the split can be used in exports.'
        ),
    )
    is_ifaa = models.BooleanField(default=False)
    # This is such a weird round we may as well special case it
    flint_round = models.BooleanField(default=False)

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
    def splits(self):
        if self.can_split:
            subround = self.subrounds.first()  # There should only be one anyway
            return [{
                'name': '%s-1' % subround.distance_short,
                'arrows': subround.arrows / 2,
            }, {
                'name': '%s-2' % subround.distance_short,
                'arrows': subround.arrows / 2,
            }]
        else:
            return [{
                'name': subround.distance_short,
                'arrows': subround.arrows,
            } for subround in self.subrounds.order_by('-distance')]

    @property
    def has_xs(self):
        return self.scoring_type == 'X'

    @property
    def has_golds(self):
        return not self.is_ifaa

    @property
    def has_elevens(self):
        return self.scoring_type == 'E'

    @property
    def gold_9s(self):
        return self.scoring_type == 'F'

    @property
    def has_hits(self):
        if self.scoring_type in ['X', 'I', 'E']:
            return False
        if self.is_ifaa:
            return False
        return True

    @property
    def score_sheet_headings(self):
        if self.scoring_type == 'X':
            return ['10+X', 'X']
        if self.scoring_type == 'E':
            return ['11s', '10s']
        elif self.scoring_type == 'I':
            return ['10s']
        elif self.is_ifaa:
            return []
        else:
            return ['H', 'G']

    @property
    def scoring_headings(self):
        if self.scoring_type == 'X':
            return ['10s+Xs', 'Xs']
        if self.scoring_type == 'E':
            return ['11s', '10s']
        elif self.scoring_type == 'I':
            return ['10s']
        else:
            return ['Hits', 'Golds']


class Bowstyle(models.Model):
    name = models.CharField(max_length=50, unique=True)
    ifaa_only = models.BooleanField(default=False)

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
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class County(models.Model):
    name = models.CharField(max_length=500, unique=True)
    short_name = models.CharField(max_length=50, unique=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'counties'
        ordering = ('short_name',)

    def __str__(self):
        return self.short_name


class Club(models.Model):
    name = models.CharField(max_length=500, unique=True)
    short_name = models.CharField(max_length=50, unique=True)

    county = models.ForeignKey(County, blank=True, null=True, on_delete=models.CASCADE)

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
    club = models.ForeignKey(Club, blank=True, null=True, on_delete=models.CASCADE)
    bowstyle = models.ForeignKey(Bowstyle, on_delete=models.CASCADE)
    age = models.CharField(max_length=1, choices=SIMPLE_AGE_CHOICES, default='S')
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
