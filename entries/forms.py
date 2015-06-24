from django.core.cache import cache
from django.db import transaction
from django import forms

from core.models import Archer, Bowstyle, Club, NOVICE_CHOICES, AGE_CHOICES, WA_AGE_CHOICES
from .models import CompetitionEntry, SessionRound, SessionEntry


class ArcherSearchForm(forms.Form):
    query = forms.CharField()

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
    club = forms.ModelChoiceField(
        queryset=Club.objects,
        required=False,
    )
    update_club = forms.BooleanField(required=False)
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
        self.fields['club'].label = 'Club (%s)' % current.club
        self.fields['bowstyle'].label = 'Bowstyle (%s)' % current.bowstyle
        self.initial['agb_number'] = archer.agb_number
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
        if len(self.session_rounds) > 1:
            self.fields['sessions'] = forms.ModelMultipleChoiceField(
                queryset=self.session_rounds,
                widget=forms.CheckboxSelectMultiple,
            )
            #if cache.get('entry-form:sessions'):
            #    self.initial['sessions'] = cache.get('entry-form:sessions')

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
        if self.cleaned_data['club'] and self.cleaned_data['update_club']:
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
        entry.club = self.cleaned_data['club'] or default.club
        entry.bowstyle = self.cleaned_data['bowstyle'] or default.bowstyle
        if self.competition.has_novices:
            entry.novice = self.cleaned_data['novice'] or default.novice
        if self.competition.has_juniors:
            entry.age = self.cleaned_data['age'] or default.age
        if self.competition.has_wa_age_groups:
            entry.wa_age = self.cleaned_data['wa_age']

    def create_session_entries(self, entry):
        if len(self.session_rounds) == 1:
            SessionEntry.objects.create(
                session_round=self.session_rounds[0],
                competition_entry=entry,
            )
        else:
            for session_round in self.cleaned_data['sessions']:
                SessionEntry.objects.create(
                    session_round=session_round,
                    competition_entry=entry,
                )


class EntryUpdateForm(EntryCreateForm):

    def __init__(self, competition, instance, **kwargs):
        self.instance = instance
        super(EntryUpdateForm, self).__init__(
            competition=competition,
            archer=instance.archer,
            **kwargs
        )
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
