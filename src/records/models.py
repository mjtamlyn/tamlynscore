from django.db import models
from django.forms import ValidationError
from django.template.defaultfilters import slugify

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
    full_name = models.CharField(max_length=300, unique=True)
    short_name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.short_name

class Subround(models.Model):
    arrows = models.PositiveIntegerField()
    distance = models.PositiveIntegerField()
    unit = models.CharField(max_length=1, choices=DISTANCE_UNITS)

    def __unicode__(self):
        return u'{0} arrows at {1} {2}'.format(self.arrows, self.distance, self.get_unit_display())

class Round(models.Model):
    name = models.CharField(max_length=100)
    subrounds = models.ManyToManyField(Subround)
    has_xs = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    @property
    def arrows(self):
        return self.subrounds.aggregate(models.Sum('arrows'))['arrows__sum']

    def get_subround(self, doz_no):
        arrows = int(doz_no) * 12
        subrounds = self.subrounds.order_by('-distance')
        counter = 0
        for subround in subrounds:
            if subround.arrows >= arrows:
                return subround
        raise Exception('There aren\'t that many dozens in that round!')

class BoundRound(models.Model):
    round_type = models.ForeignKey(Round)
    competition = models.ForeignKey('Competition')
    use_individual_arrows = models.BooleanField(default=False)

    def __unicode__(self):
        return u'{0} at {1}'.format(self.round_type, self.competition)

    @property
    def arrows(self):
        return self.round_type.arrows

class Competition(models.Model):
    date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    slug = models.SlugField(editable=False, unique=True)

    rounds = models.ManyToManyField(Round, through=BoundRound)
    tournament = models.ForeignKey(Tournament)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def clean(self, *args, **kwargs):
        if self.end_date is None:
            self.end_date = self.date
        self.slug = slugify('{0} {1}'.format(self.tournament, self.date.year))
        return super(Competition, self).clean(*args, **kwargs)

    def full_results(self):
        ordering = ['bowstyle', 'archer__gender', '-score', '-hits', '-golds']
        results = {}
        for the_round in self.boundround_set.all():
            all_scores = the_round.entry_set.select_related().order_by(*ordering)
            results[the_round] = []
            for key, group in groupby(all_scores, lambda s: s.get_classification()):
                results[the_round].append({
                    'round': the_round.round_type,
                    'class': key,
                    'scores': list(group)
                })
        return results

    def __unicode__(self):
        return u'{0}: {1}'.format(self.tournament, self.date.year)

    class Meta:
        unique_together = ('date', 'tournament')

class Bowstyle(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return self.name

class Club(models.Model):
    name = models.CharField(max_length=500, unique=True)
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
            'id': self.pk,
            'name': self.name,
            'gender': self.get_gender_display(),
            'club': self.club.pk,
            'bowstyle': self.bowstyle.pk,
        })

    class Meta:
        unique_together = ('name', 'club')

class Entry(models.Model):
    shot_round = models.ForeignKey(BoundRound)

    archer = models.ForeignKey(Archer)
    club = models.ForeignKey(Club)
    bowstyle = models.ForeignKey(Bowstyle)

    score = models.IntegerField(blank=True, null=True)
    hits = models.IntegerField(blank=True, null=True)
    golds = models.IntegerField(blank=True, null=True)
    xs = models.IntegerField(blank=True, null=True)

    retired = models.BooleanField(default=False)
    target = models.CharField(max_length=10, blank=True, null=True)

    def get_classification(self):
        return u'{0} {1}'.format(self.bowstyle, self.archer.get_gender_display())

    def update_totals(self):
        self.score = self.arrow_set.aggregate(models.Sum('score'))['score__sum']
        self.golds = self.arrow_set.filter(score=10).count()
        self.hits = self.arrow_set.exclude(score=0).count()
        if self.shot_round.round_type.has_xs:
            self.xs = self.arrow_set.filter(is_x=True).count()
        self.save()

    def __unicode__(self):
        return u'{0} at {1}'.format(self.archer, self.shot_round.competition)

    class Meta:
        verbose_name_plural = 'entries'
        unique_together = ('archer', 'shot_round')

class Arrow(models.Model):
    subround = models.ForeignKey(Subround)
    entry = models.ForeignKey(Entry)
    score = models.PositiveIntegerField()
    arrow_of_round = models.PositiveIntegerField()
    is_x = models.BooleanField(default=False)

    def __unicode__(self):
        if self.is_x:
            return u'X'
        if self.score == 0:
            return u'M'
        return unicode(self.score)

    def clean(self):
        if self.arrow_of_round > self.subround.arrows:
            raise ValidationError('You can\'t have arrow {0} in a subround of {1} arrows.'.format(self.arrow_of_round, self.subround.arrows))

    class Meta:
        unique_together = ('subround', 'arrow_of_round', 'entry')
