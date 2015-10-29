import math

from django.db import models
from django.template.defaultfilters import slugify

from core.models import Archer, Bowstyle, Club, County, Round, AGE_CHOICES, WA_AGE_CHOICES, NOVICE_CHOICES

from scores.result_modes import get_result_modes


SCORING_FULL = 'F'
SCORING_DOZENS = 'D'
SCORING_TOTALS = 'T'
SCORING_SYSTEMS = (
    (SCORING_FULL, 'Full running slips'),
    (SCORING_DOZENS, 'Dozen running slips'),
    (SCORING_TOTALS, 'Totals only'),
)


class Tournament(models.Model):
    full_name = models.CharField(max_length=300, unique=True)
    short_name = models.CharField(max_length=20)

    host_club = models.ForeignKey(Club, blank=True, null=True)

    def __str__(self):
        return self.short_name


class Sponsor(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='sponsors')

    def __str__(self):
        return self.name


class Competition(models.Model):
    tournament = models.ForeignKey(Tournament)
    admins = models.ManyToManyField('core.User', blank=False)

    date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    slug = models.SlugField(editable=False, unique=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    sponsors = models.ManyToManyField(Sponsor, blank=True)

    has_novices = models.BooleanField(default=False)
    has_juniors = models.BooleanField(default=False)
    has_wa_age_groups = models.BooleanField(default=False)
    novices_in_experienced_teams = models.BooleanField(default=False)
    exclude_later_shoots = models.BooleanField(default=False, help_text='Only the first session can count for results')
    use_county_teams = models.BooleanField(default=False)
    strict_b_teams = models.BooleanField(default=False, help_text='e.g. BUTC')
    strict_c_teams = models.BooleanField(default=False, help_text='e.g. BUTC')
    allow_incomplete_teams = models.BooleanField(default=True)
    team_size = models.PositiveIntegerField(default=4)
    novice_team_size = models.PositiveIntegerField(blank=True, null=True)
    compound_team_size = models.PositiveIntegerField(blank=True, null=True, default=None)
    junior_team_size = models.PositiveIntegerField(blank=True, null=True, default=None)
    force_mixed_teams = models.BooleanField(default=False)
    split_gender_teams = models.BooleanField(default=False, help_text='Does not affect novice teams')
    combine_rounds_for_team_scores = models.BooleanField(default=False)

    class Meta:
        unique_together = ('date', 'tournament')

    def __str__(self):
        return u'{0} {1}'.format(self.tournament, self.date.year)

    def clean(self, *args, **kwargs):
        if self.end_date is None:
            self.end_date = self.date
        self.slug = slugify('{0} {1}'.format(self.tournament, self.date.year))
        return super(Competition, self).clean(*args, **kwargs)

    def sessions_with_rounds(self):
        try:
            return self._sessions_with_rounds
        except AttributeError:
            sessions = self.session_set.order_by('start').prefetch_related('sessionround_set')
            self._sessions_with_rounds = sessions
            return sessions

    def has_olympic(self):
        return self.session_set.filter(olympicsessionround__isnull=False).exists()

    def is_admin(self, user):
        if user.is_anonymous():
            return False
        if user.is_superuser:
            return True
        return self.admins.filter(pk=user.pk).exists()


class ResultsMode(models.Model):
    competition = models.ForeignKey(Competition, related_name='result_modes')
    mode = models.CharField(max_length=31, choices=tuple(get_result_modes()))
    leaderboard_only = models.BooleanField(default=False)
    json = models.TextField(blank=True, default='')

    class Meta:
        unique_together = ('competition', 'mode')

    def __str__(self):
        return str(self.get_mode_display())


class Session(models.Model):
    competition = models.ForeignKey(Competition)
    start = models.DateTimeField()

    scoring_system = models.CharField(max_length=1, choices=SCORING_SYSTEMS)
    archers_per_target = models.IntegerField()
    arrows_entered_per_end = models.IntegerField(default=12)

    def __str__(self):
        return u'{0} - {1}'.format(self.competition, self.start)

    class Meta:
        ordering = ['start']

    @property
    def details(self):
        details = ['A', 'B', 'C', 'D', 'E', 'F']
        return details[:self.archers_per_target]

    @property
    def input_view_name(self):
        return {
            SCORING_FULL: 'input_arrows',
            SCORING_DOZENS: 'input_dozens',
            SCORING_TOTALS: 'input_arrows',  # FIXME
        }[self.scoring_system]

    def target_list(self):
        target_allocations = TargetAllocation.objects.filter(session_entry__session_round__session=self).select_related()
        minimum_boss = target_allocations.aggregate(models.Min('boss'))['boss__min']
        if not minimum_boss:
            minimum_boss = 1
        current_bosses = target_allocations.aggregate(models.Max('boss'))['boss__max']
        bosses = range(minimum_boss, current_bosses + 1)

        allocations_lookup = dict([('{0}{1}'.format(allocation.boss, allocation.target), allocation) for allocation in target_allocations])

        targets = []
        for boss in bosses:
            for detail in self.details:
                target = '{0}{1}'.format(boss, detail)
                targets.append((target, allocations_lookup.get(target, None)))
        return targets


class SessionRound(models.Model):
    session = models.ForeignKey(Session)
    shot_round = models.ForeignKey(Round)

    def target_list(self):
        entries = self.sessionentry_set.count()
        archers_per_target = self.session.archers_per_target
        needed_bosses = int(math.ceil(entries / float(archers_per_target)))
        current_target_allocations = TargetAllocation.objects.filter(session_entry__session_round=self).select_related()
        # FIXME: Don't do this for making target lists
        minimum_boss = current_target_allocations.aggregate(models.Min('boss'))['boss__min']
        if not minimum_boss:
            minimum_boss = 1
        current_bosses = current_target_allocations.aggregate(models.Max('boss'))['boss__max']
        bosses = range(minimum_boss, max(needed_bosses, current_bosses) + 1)

        details = self.session.details

        allocations_lookup = dict([('{0}{1}'.format(allocation.boss, allocation.target), allocation) for allocation in current_target_allocations])

        targets = []
        for boss in bosses:
            for detail in details:
                target = '{0}{1}'.format(boss, detail)
                targets.append((target, allocations_lookup.get(target, None)))
        return targets

    def target_list_pdf(self, lunch=False, whole_session=False):
        competition = self.session.competition
        if whole_session:
            current_target_allocations = TargetAllocation.objects.filter(session_entry__session_round__session=self.session).select_related()
        else:
            current_target_allocations = TargetAllocation.objects.filter(session_entry__session_round=self).select_related()
        minimum_boss = current_target_allocations.aggregate(models.Min('boss'))['boss__min']
        current_bosses = current_target_allocations.aggregate(models.Max('boss'))['boss__max']
        if not current_bosses:
            return []
        bosses = range(minimum_boss, current_bosses + 1)
        allocations_lookup = dict([('{0}{1}'.format(allocation.boss, allocation.target), allocation) for allocation in current_target_allocations])
        details = self.session.details

        targets = []
        for boss in bosses:
            for detail in details:
                target = '{0}{1}'.format(boss, detail)
                allocation = allocations_lookup.get(target, None)
                if allocation:
                    entry = allocation.session_entry.competition_entry
                    shot_round = allocation.session_entry.session_round.shot_round
                    allocation = (
                        entry.archer,
                        entry.team_name(short_form=False),
                    )
                    if lunch:
                        allocation += (None, None, None)
                    else:
                        allocation += (
                            entry.archer.get_gender_display(),
                            entry.bowstyle,
                        )
                        if competition.has_juniors:
                            allocation += (
                                entry.get_age_display(),
                            )
                        if competition.has_novices:
                            allocation += (
                                entry.get_novice_display(),
                            )
                        if competition.has_wa_age_groups and entry.wa_age:
                            allocation += (
                                entry.get_wa_age_display(),
                            )
                    if whole_session:
                        allocation += (shot_round.name,)
                    targets.append((target,) + allocation)
                else:
                    targets.append((target, None))
        return targets

    def __str__(self):
        return u'{0}, {1}'.format(self.session, self.shot_round)


class CompetitionEntry(models.Model):
    competition = models.ForeignKey(Competition)

    archer = models.ForeignKey(Archer)
    club = models.ForeignKey(Club, blank=True, null=True)
    county = models.ForeignKey(County, blank=True, null=True)
    bowstyle = models.ForeignKey(Bowstyle)
    age = models.CharField(max_length=1, choices=AGE_CHOICES, default='S')
    wa_age = models.CharField(max_length=1, choices=WA_AGE_CHOICES, default='', blank=True)
    novice = models.CharField(max_length=1, choices=NOVICE_CHOICES, default='E')

    guest = models.BooleanField(default=False)
    b_team = models.BooleanField(default=False)
    c_team = models.BooleanField(default=False)

    def __str__(self):
        return u'{0} at {1}'.format(self.archer, self.competition)

    class Meta:
        verbose_name_plural = 'competition entries'

    def code(self):
        gender = self.archer.gender
        bowstyle = self.bowstyle.name[0]
        return gender + bowstyle

    def category(self):
        junior = 'Junior ' if self.competition.has_juniors and self.age == 'J' else ''
        novice = 'Novice ' if self.competition.has_novices and self.novice == 'N' else ''
        return u'{2}{3}{0} {1}'.format(self.archer.get_gender_display(), self.bowstyle, junior, novice)

    def team_name(self, short_form=True):
        if self.club_id:
            name = self.club.short_name if short_form else self.club.name
        elif self.county_id:
            name = self.county.short_name if short_form else self.county.name
        else:
            return ''
        if self.b_team or self.c_team:
            return '%s (%s)' % (name, 'B' if self.b_team else 'C')
        return name


class SessionEntry(models.Model):
    competition_entry = models.ForeignKey(CompetitionEntry)
    session_round = models.ForeignKey(SessionRound)

    present = models.BooleanField(default=False)
    index = models.PositiveIntegerField(default=1)

    def __str__(self):
        return u'{0} - {1}'.format(self.competition_entry, self.session_round.shot_round)

    class Meta:
        verbose_name_plural = 'session entries'


class TargetAllocation(models.Model):
    session_entry = models.OneToOneField('SessionEntry')
    boss = models.PositiveIntegerField()
    target = models.CharField(max_length=1)

    def __str__(self):
        return u'{0}{1} - {2}'.format(self.boss, self.target, self.session_entry)
