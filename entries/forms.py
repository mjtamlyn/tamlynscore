from django.db import transaction
from django import forms

from core.models import Archer, Bowstyle, Club, NOVICE_CHOICES, AGE_CHOICES
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

    def __init__(self, archer, competition, **kwargs):
        super(EntryCreateForm, self).__init__(**kwargs)
        self.archer = archer
        self.competition = competition
        self.session_rounds = SessionRound.objects.filter(session__competition=competition)
        self.fields['club'].label = 'Club (%s)' % self.archer.club
        self.fields['bowstyle'].label = 'Bowstyle (%s)' % self.archer.bowstyle
        if self.competition.has_novices:
            self.fields['novice'] = forms.ChoiceField(
                label='Experienced/Novice (%s)' % self.archer.get_novice_display(),
                choices=(('', '---------'),) + NOVICE_CHOICES,
                required=False,
            )
            self.fields['update_novice'] = forms.BooleanField(required=False)
        if self.competition.has_juniors:
            self.fields['age'] = forms.ChoiceField(
                label='Age (%s)' % self.archer.get_age_display(),
                choices=(('', '---------'),) + AGE_CHOICES,
                required=False,
            )
            self.fields['update_age'] = forms.BooleanField(required=False)
        if len(self.session_rounds) > 1:
            self.fields['sessions'] = forms.ModelMultipleChoiceField(
                queryset=self.session_rounds,
                widget=forms.CheckboxSelectMultiple,
            )

    def save(self):
        with transaction.atomic():
            self.update_archer()
            entry = self.create_competition_entry()
            self.create_session_entries(entry)

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
        if changed:
            self.archer.save()

    def create_competition_entry(self):
        club = self.cleaned_data['club'] or self.archer.club
        bowstyle = self.cleaned_data['bowstyle'] or self.archer.bowstyle
        extra_params = {}
        if self.competition.has_novices:
            extra_params['novice'] = self.cleaned_data['novice'] or self.archer.novice
        if self.competition.has_juniors:
            extra_params['age'] = self.cleaned_data['age'] or self.archer.age
        return CompetitionEntry.objects.create(
            competition=self.competition,
            archer=self.archer,
            club=club,
            bowstyle=bowstyle,
            **extra_params
        )

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
