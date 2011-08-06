from django.db import models
from django.template.defaultfilters import slugify

from core.models import Archer, Bowstyle, Club, Round, AGE_CHOICES, NOVICE_CHOICES

import math

SCORING_SYSTEMS = (
    ('F', 'Full running slips'),
    ('D', 'Dozen running slips'),
    ('T', 'Totals only'),
)

class Tournament(models.Model):
    full_name = models.CharField(max_length=300, unique=True)
    short_name = models.CharField(max_length=20)

    host_club = models.ForeignKey(Club)

    def __unicode__(self):
        return self.short_name

class Competition(models.Model):
    tournament = models.ForeignKey(Tournament)

    date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    slug = models.SlugField(editable=False, unique=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def clean(self, *args, **kwargs):
        if self.end_date is None:
            self.end_date = self.date
        self.slug = slugify('{0} {1}'.format(self.tournament, self.date.year))
        return super(Competition, self).clean(*args, **kwargs)

    def sessions_with_rounds(self):
        sessions = self.session_set.annotate(count=models.Count('sessionround')).filter(
                count__gt=0).order_by('start')
        return sessions

    def __unicode__(self):
        return u'{0} {1}'.format(self.tournament, self.date.year)

    class Meta:
        unique_together = ('date', 'tournament')

class Session(models.Model):
    competition = models.ForeignKey(Competition)
    start = models.DateTimeField()

    scoring_system = models.CharField(max_length=1, choices=SCORING_SYSTEMS)
    archers_per_target = models.IntegerField()

    def __unicode__(self):
        return u'{0} - {1}'.format(self.competition, self.start)

    def details(self):
        details = ['A', 'B', 'C', 'D', 'E', 'F']
        return details[:self.archers_per_target]

class SessionRound(models.Model):
    session = models.ForeignKey(Session)
    shot_round = models.ForeignKey(Round)

    def target_list(self):
        entries = self.sessionentry_set.count()
        archers_per_target = self.session.archers_per_target
        needed_bosses = int(math.ceil(entries / float(archers_per_target)))
        current_target_allocations = TargetAllocation.objects.filter(session_entry__session_round=self)
        #FIXME: Don't do this for making target lists
        minimum_boss = current_target_allocations.aggregate(models.Min('boss'))['boss__min']
        if not minimum_boss:
            minimum_boss = 1
        current_bosses = current_target_allocations.aggregate(models.Max('boss'))['boss__max']
        bosses = range(minimum_boss, max(needed_bosses, current_bosses) + 1)

        details = self.session.details()

        allocations_lookup = dict([('{0}{1}'.format(allocation.boss, allocation.target), allocation) for allocation in current_target_allocations])

        targets = []
        for boss in bosses:
            for detail in details:
                target = '{0}{1}'.format(boss, detail)
                targets.append((target, allocations_lookup.get(target, None)))
        return targets

    def target_list_pdf(self, lunch=False):
        current_target_allocations = TargetAllocation.objects.filter(session_entry__session_round=self)
        minimum_boss = current_target_allocations.aggregate(models.Min('boss'))['boss__min']
        current_bosses = current_target_allocations.aggregate(models.Max('boss'))['boss__max']
        if not current_bosses:
            return []
        bosses = range(minimum_boss, current_bosses + 1)
        allocations_lookup = dict([('{0}{1}'.format(allocation.boss, allocation.target), allocation) for allocation in current_target_allocations])
        details = self.session.details()

        targets = []
        for boss in bosses:
            for detail in details:
                target = '{0}{1}'.format(boss, detail)
                allocation = allocations_lookup.get(target, None)
                if allocation:
                    entry = allocation.session_entry.competition_entry
                    allocation = (
                            entry.archer,
                            entry.club.name,
                    )
                    if lunch:
                        allocation += (None, None, None)
                    else:
                        allocation += (
                                entry.archer.get_gender_display(),
                                entry.bowstyle,
                                entry.get_age_display(),
                        )
                    targets.append((target,) + allocation)
                else:
                    targets.append((target, None))
        return targets

    def __unicode__(self):
        return u'{0}, {1}'.format(self.session, self.shot_round)

class CompetitionEntry(models.Model):
    competition = models.ForeignKey(Competition)

    archer = models.ForeignKey(Archer)
    club = models.ForeignKey(Club)
    bowstyle = models.ForeignKey(Bowstyle)
    age = models.CharField(max_length=1, choices=AGE_CHOICES)
    novice = models.CharField(max_length=1, choices=NOVICE_CHOICES)

    def __unicode__(self):
        return u'{0} at {1}'.format(self.archer, self.competition)

    class Meta:
        verbose_name_plural = 'competition entries'

    def rounds_entered(self):
        rounds = []
        for session in self.competition.sessions_with_rounds():
            entries = self.sessionentry_set.filter(session_round__session=session)
            if entries:
                rounds.append(entries[0].session_round.shot_round)
            else:
                rounds.append(u'-')
        return rounds

    def code(self):
        gender = self.archer.gender
        bowstyle = self.bowstyle.name[0]
        return gender + bowstyle

class SessionEntry(models.Model):
    competition_entry = models.ForeignKey(CompetitionEntry)
    session_round = models.ForeignKey(SessionRound)

    present = models.BooleanField(default=False)

    def __unicode__(self):
        return u'{0} - {1}'.format(self.competition_entry, self.session_round.shot_round)

    class Meta:
        verbose_name_plural = 'session entries'

class TargetAllocation(models.Model):
    session_entry = models.ForeignKey(SessionEntry)
    boss = models.PositiveIntegerField()
    target = models.CharField(max_length=1)

    def __unicode__(self):
        return u'{0}{1} - {2}'.format(self.boss, self.target, self.session_entry)


