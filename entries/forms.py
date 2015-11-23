from django.core.cache import cache
from django.db import transaction
from django import forms

from core.models import Archer, Bowstyle, Club, County, Round, NOVICE_CHOICES, AGE_CHOICES, WA_AGE_CHOICES, AGB_AGE_CHOICES
from scores.result_modes import get_result_modes, ByRound

from .models import Tournament, Competition, CompetitionEntry, Session, SessionRound, SessionEntry, SCORING_SYSTEMS, SCORING_FULL


class CompetitionForm(forms.Form):
    # Fields about the shoot itself
    full_name = forms.CharField(max_length=300)
    short_name = forms.CharField(max_length=20)
    date = forms.DateField()
    end_date = forms.DateField(required=False)

    # Fields about sessions and rounds shot in them
    scoring_system = forms.ChoiceField(choices=SCORING_SYSTEMS, initial=SCORING_FULL)
    archers_per_target = forms.IntegerField(initial=4)
    arrows_entered_per_end = forms.IntegerField(initial=12, help_text='Number of arrow values included on each running slip')
    session_1_time = forms.DateTimeField(label='Session time')
    session_1_rounds = forms.ModelMultipleChoiceField(Round.objects, label='Rounds')
    session_2_time = forms.DateTimeField(required=False, label='Session time')
    session_2_rounds = forms.ModelMultipleChoiceField(Round.objects, required=False, label='Rounds')
    session_3_time = forms.DateTimeField(required=False, label='Session time')
    session_3_rounds = forms.ModelMultipleChoiceField(Round.objects, required=False, label='Rounds')
    session_4_time = forms.DateTimeField(required=False, label='Session time')
    session_4_rounds = forms.ModelMultipleChoiceField(Round.objects, required=False, label='Rounds')
    session_5_time = forms.DateTimeField(required=False, label='Session time')
    session_5_rounds = forms.ModelMultipleChoiceField(Round.objects, required=False, label='Rounds')
    session_6_time = forms.DateTimeField(required=False, label='Session time')
    session_6_rounds = forms.ModelMultipleChoiceField(Round.objects, required=False, label='Rounds')

    # Fields about result types
    result_modes = forms.MultipleChoiceField(choices=get_result_modes, widget=forms.CheckboxSelectMultiple, initial=[ByRound.slug])
    leaderboard_only_modes = forms.MultipleChoiceField(choices=get_result_modes, widget=forms.CheckboxSelectMultiple, required=False)

    # Fields about individual results
    has_guests = forms.BooleanField(required=False, label='Allow guest entries')
    has_novices = forms.BooleanField(required=False, label='Use a novice category')
    has_juniors = forms.BooleanField(required=False, label='Use a general junior category')
    has_wa_age_groups = forms.BooleanField(required=False, label='Use WA style age groups')
    has_agb_age_groups = forms.BooleanField(required=False, label='Use ArcheryGB style age groups')
    exclude_later_shoots = forms.BooleanField(required=False, help_text='Only the first session can count for results')

    # Fields about team results
    team_size = forms.IntegerField(required=False)
    allow_incomplete_teams = forms.BooleanField(required=False, initial=True, help_text='Print results for teams without a full complement of archers')
    combine_rounds_for_team_scores = forms.BooleanField(required=False, help_text='Base each archer\'s contribution to the team on their aggregate score accross all rounds')
    force_mixed_teams = forms.BooleanField(required=False, help_text='Require a team member of each gender')
    split_gender_teams = forms.BooleanField(required=False, help_text='Split teams by gender. Does not affect novice teams')
    use_county_teams = forms.BooleanField(required=False, help_text='Group teams by county instead of club')
    strict_b_teams = forms.BooleanField(required=False, help_text='Allow two separate team entries from a club with predetermined archers')
    strict_c_teams = forms.BooleanField(required=False, help_text='Allow three separate team entries from a club with predetermined archers')
    novice_team_size = forms.IntegerField(required=False)
    novices_in_experienced_teams = forms.BooleanField(required=False, help_text='Allow novice scores to count in experienced results')
    compound_team_size = forms.IntegerField(required=False)
    junior_team_size = forms.IntegerField(required=False)

    CONFIG_FIELDS = [
        'has_guests',
        'has_novices',
        'has_juniors',
        'has_wa_age_groups',
        'has_agb_age_groups',
        'exclude_later_shoots',
        'team_size',
        'allow_incomplete_teams',
        'combine_rounds_for_team_scores',
        'force_mixed_teams',
        'split_gender_teams',
        'use_county_teams',
        'strict_b_teams',
        'strict_c_teams',
        'novice_team_size',
        'novices_in_experienced_teams',
        'compound_team_size',
        'junior_team_size',
    ]

    def __init__(self, instance=None, initial=None, **kwargs):
        if initial is None:
            initial = {}
        if instance is None:
            instance = Competition()
        else:
            initial = self.get_initial(initial, instance)
        self.instance = instance
        super(CompetitionForm, self).__init__(initial=initial, **kwargs)

    def get_initial(self, initial, instance):
        initial['full_name'] = instance.tournament.full_name
        initial['short_name'] = instance.tournament.short_name
        initial['date'] = instance.date
        initial['end_date'] = instance.end_date

        sessions = instance.session_set.order_by('start')
        initial['archers_per_target'] = sessions[0].archers_per_target
        initial['scoring_system'] = sessions[0].scoring_system
        initial['arrows_entered_per_end'] = sessions[0].arrows_entered_per_end
        for i, session in enumerate(sessions, 1):
            initial['session_%s_time' % i] = session.start
            initial['session_%s_rounds' % i] = list(session.sessionround_set.values_list('shot_round', flat=True))

        initial['result_modes'] = list(instance.result_modes.values_list('mode', flat=True))
        for field in self.CONFIG_FIELDS:
            initial[field] = getattr(instance, field)
        return initial

    def clean(self):
        self.clean_session_fields()

    def clean_session_fields(self):
        # No need to validate first pair as they're both required
        for i in range(2, 7):
            time = self.cleaned_data.get('session_%s_time' % i)
            rounds = self.cleaned_data.get('session_%s_rounds' % i)
            if (not time and rounds) or (time and not rounds):
                self.add_error('session_%s_time' % i,
                    forms.ValidationError('Must have start and rounds for a session', code='session_match')
                )
        times = [self.cleaned_data.get('session_%s_time' % i) for i in range(1, 7)]
        current_time = times[0]
        for i, time in enumerate(times[1:], 1):
            if time is None:
                if any(times[i:]):
                    self.add_error('session_1_time',
                        forms.ValidationError('Must not have gaps in sessions', code='session_order')
                    )
                break
            elif time < current_time:
                self.add_error('session_1_time',
                    forms.ValidationError('Session times must be in order', code='session_order')
                )
            current_time = time

    def save(self):
        self.handle_shoot_fields()
        self.instance.clean()
        self.instance.save()
        self.handle_session_fields()
        self.handle_result_mode_fields()
        return self.instance

    def handle_shoot_fields(self):
        tournament, _ = Tournament.objects.get_or_create(
            full_name=self.cleaned_data['full_name'],
            defaults={'short_name': self.cleaned_data['short_name']},
        )
        tournament.save()
        self.instance.tournament = tournament
        self.instance.date = self.cleaned_data['date']
        for field in self.CONFIG_FIELDS:
            setattr(self.instance, field, self.cleaned_data[field])

    def handle_session_fields(self):
        sessions = self.instance.session_set.order_by('start')
        for i in range(1, 7):
            try:
                session = sessions[i - 1]
            except IndexError:
                session = Session(competition=self.instance)
            session_time = self.cleaned_data['session_%s_time' % i]
            if session_time is None:
                if session.pk:
                    session.delete()
                continue
            session.start = session_time
            session.scoring_system = self.cleaned_data['scoring_system']
            session.archers_per_target = self.cleaned_data['archers_per_target']
            session.arrows_entered_per_end = self.cleaned_data['arrows_entered_per_end']
            session.save()
            rounds_to_be_shot = {r.pk for r in self.cleaned_data['session_%s_rounds' % i]}
            existing_session_rounds = session.sessionround_set.values_list('shot_round', flat=True)
            for rnd in existing_session_rounds:
                if rnd in rounds_to_be_shot:
                    rounds_to_be_shot.remove(rnd)
                else:
                    session.sessionround_set.filter(shot_round=rnd).delete()
            for rnd in rounds_to_be_shot:
                session.sessionround_set.create(shot_round_id=rnd)

    def handle_result_mode_fields(self):
        modes = set(self.cleaned_data['result_modes'])
        existing_result_modes = self.instance.result_modes.values_list('mode', flat=True)
        for mode in existing_result_modes:
            if mode in modes:
                modes.remove(mode)
            else:
                self.instance.result_modes.filter(mode=mode).delete()
        for mode in modes:
            self.instance.result_modes.create(mode=mode)


class ArcherSearchForm(forms.Form):
    query = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(ArcherSearchForm, self).__init__(*args, **kwargs)
        self.fields['query'].widget.attrs.update({'autofocus': ''})

    def get_archers(self):
        # One day, do this with expressions and/or contrib.postgres. Please.
        term = self.cleaned_data['query']
        return Archer.objects.filter(club__name__isnull=False).extra(
            select={
                'similarity': 'similarity("core_archer"."name", %s)',
                'club_similarity': 'similarity("core_club"."name", %s)',
                'club_shortname_similarity': 'similarity("core_club"."short_name", %s)',
            },
            select_params=[term, term, term],
            where=['"core_archer"."name" %% %s OR "core_club"."name" %% %s OR "core_club"."short_name" %% %s'],
            params=[term, term, term],
            order_by=['-similarity', '-club_similarity', '-club_shortname_similarity'],
        )


class EntryCreateForm(forms.Form):
    bowstyle = forms.ModelChoiceField(
        queryset=Bowstyle.objects,
        required=False,
    )
    update_bowstyle = forms.BooleanField(required=False)
    agb_number = forms.IntegerField(required=False, label='ArcheryGB number')

    def __init__(self, archer, competition, **kwargs):
        super(EntryCreateForm, self).__init__(**kwargs)
        self.archer = archer
        self.competition = competition
        self.session_rounds = SessionRound.objects.filter(session__competition=competition)
        current = self.get_current_obj()
        self.fields['bowstyle'].label = 'Bowstyle (%s)' % current.bowstyle
        self.initial['agb_number'] = archer.agb_number
        if self.competition.use_county_teams:
            self.fields['county'] = forms.ModelChoiceField(
                label='County (%s)' % current.club.county if current.club and current.club.county else 'County',
                queryset=County.objects,
                required=False,
            )
            self.fields['county'].widget.attrs.update({'autofocus': ''})
        else:
            self.fields['club'] = forms.ModelChoiceField(
                label='Club (%s)' % current.club if current.club else 'Club',
                queryset=Club.objects,
                required=False,
            )
            self.fields['club'].widget.attrs.update({'autofocus': ''})
            self.fields['update_club'] = forms.BooleanField(required=False)
        if self.competition.has_novices:
            self.fields['novice'] = forms.ChoiceField(
                label='Experienced/Novice (%s)' % current.get_novice_display(),
                choices=(('', '---------'),) + NOVICE_CHOICES,
                required=False,
            )
            self.fields['update_novice'] = forms.BooleanField(required=False)
        if self.competition.has_juniors:
            self.fields['age'] = forms.ChoiceField(
                label='Age (%s)' % current.get_age_display(),
                choices=(('', '---------'),) + AGE_CHOICES,
                required=False,
            )
            self.fields['update_age'] = forms.BooleanField(required=False)
        if self.competition.has_wa_age_groups:
            self.fields['wa_age'] = forms.ChoiceField(
                label='Age Group (%s)' % current.get_wa_age_display(),
                choices=WA_AGE_CHOICES,
                required=False,
            )
            self.fields['update_wa_age'] = forms.BooleanField(required=False)
        if self.competition.has_agb_age_groups:
            self.fields['agb_age'] = forms.ChoiceField(
                label='Age Group (%s)' % current.get_agb_age_display(),
                choices=AGB_AGE_CHOICES,
                required=False,
            )
            self.fields['update_agb_age'] = forms.BooleanField(required=False)
        if len(self.session_rounds) > 1:
            self.fields['sessions'] = forms.ModelMultipleChoiceField(
                queryset=self.session_rounds,
                widget=forms.CheckboxSelectMultiple,
            )
        if self.competition.has_guests:
            self.fields['guest'] = forms.BooleanField(required=False)

    def get_current_obj(self):
        return self.archer

    def save(self):
        with transaction.atomic():
            self.update_archer()
            entry = self.create_competition_entry()
            self.create_session_entries(entry)
        if len(self.session_rounds) > 1:
            cache.set('entry-form:sessions', self.cleaned_data['sessions'])

    def update_archer(self):
        changed = False
        if not self.competition.use_county_teams and self.cleaned_data['club'] and self.cleaned_data['update_club']:
            self.archer.club = self.cleaned_data['club']
            changed = True
        if self.cleaned_data['bowstyle'] and self.cleaned_data['update_bowstyle']:
            self.archer.bowstyle = self.cleaned_data['bowstyle']
            changed = True
        if self.competition.has_novices and self.cleaned_data['novice'] and self.cleaned_data['update_novice']:
            self.archer.novice = self.cleaned_data['novice']
            changed = True
        if self.competition.has_juniors and self.cleaned_data['age'] and self.cleaned_data['update_age']:
            self.archer.age = self.cleaned_data['age']
            changed = True
        if self.competition.has_wa_age_groups and self.cleaned_data['wa_age'] and self.cleaned_data['update_wa_age']:
            self.archer.wa_age = self.cleaned_data['wa_age']
            changed = True
        if self.competition.has_agb_age_groups and self.cleaned_data['agb_age'] and self.cleaned_data['update_agb_age']:
            self.archer.agb_age = self.cleaned_data['agb_age']
            changed = True
        if not self.cleaned_data['agb_number'] == self.archer.agb_number:
            self.archer.agb_number = self.cleaned_data['agb_number']
            changed = True
        if changed:
            self.archer.save()

    def create_competition_entry(self):
        entry = CompetitionEntry(
            competition=self.competition,
            archer=self.archer,
        )
        self.set_entry_data(entry)
        entry.save()
        return entry

    def set_entry_data(self, entry):
        default = self.get_current_obj()
        if self.competition.use_county_teams:
            entry.county = self.cleaned_data['county'] or (default.club.county if default.club else None)
        else:
            entry.club = self.cleaned_data['club'] or default.club
        entry.bowstyle = self.cleaned_data['bowstyle'] or default.bowstyle
        if self.competition.has_novices:
            entry.novice = self.cleaned_data['novice'] or default.novice
        if self.competition.has_juniors:
            entry.age = self.cleaned_data['age'] or default.age
        if self.competition.has_wa_age_groups:
            entry.wa_age = self.cleaned_data['wa_age']
        if self.competition.has_agb_age_groups:
            entry.agb_age = self.cleaned_data['agb_age']
            if entry.agb_age:
                entry.age = 'J'
        if self.competition.has_guests:
            entry.guest = self.cleaned_data['guest']

    def create_session_entries(self, entry):
        if len(self.session_rounds) == 1:
            SessionEntry.objects.create(
                session_round=self.session_rounds[0],
                competition_entry=entry,
            )
        else:
            for i, session_round in enumerate(self.cleaned_data['sessions'], 1):
                SessionEntry.objects.create(
                    session_round=session_round,
                    competition_entry=entry,
                    index=i,
                )


class EntryUpdateForm(EntryCreateForm):

    def __init__(self, competition, instance, **kwargs):
        self.instance = instance
        super(EntryUpdateForm, self).__init__(
            competition=competition,
            archer=instance.archer,
            **kwargs
        )
        self.initial['guest'] = instance.guest
        self.initial['sessions'] = [se.session_round for se in self.instance.sessionentry_set.all()]

    def get_current_obj(self):
        return self.instance

    def save(self):
        with transaction.atomic():
            self.update_archer()
            self.set_entry_data(self.instance)
            self.instance.save()
            self.update_session_entries(self.instance)

    def update_session_entries(self, entry):
        if len(self.session_rounds) > 1:
            existing_rounds = self.initial['sessions']
            for session_round in self.cleaned_data['sessions']:
                if session_round in existing_rounds:
                    existing_rounds.remove(session_round)
                else:
                    SessionEntry.objects.create(
                        session_round=session_round,
                        competition_entry=entry,
                    )
            if existing_rounds:
                entry.sessionentry_set.filter(session_round__in=existing_rounds).delete()
        for i, sr in enumerate(entry.sessionentry_set.all(), 1):
            sr.index = i
            sr.save()
