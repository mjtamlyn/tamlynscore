from django.db import models
from django.template.defaultfilters import slugify

class Tournament(models.Model):
    full_name = models.CharField(max_length=300, unique=True)
    short_name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.short_name

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

class BoundRound(models.Model):
    round_type = models.ForeignKey(Round)
    competition = models.ForeignKey('Competition')
    use_individual_arrows = models.BooleanField(default=False)

    def __unicode__(self):
        return u'{0} at {1}'.format(self.round_type, self.competition)

    @property
    def arrows(self):
        return self.round_type.arrows

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

