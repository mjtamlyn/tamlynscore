from django.db import transaction
from django import forms

from core.models import Archer, Club
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

    def __init__(self, archer, competition, **kwargs):
        super(EntryCreateForm, self).__init__(**kwargs)
        self.archer = archer
        self.competition = competition
        self.session_rounds = SessionRound.objects.filter(session__competition=competition)
        if len(self.session_rounds) > 1:
            self.fields['sessions'] = forms.ModelMultipleChoiceField(
                queryset=self.session_rounds,
                widget=forms.CheckboxSelectMultiple,
            )
        self.fields['club'].label = 'Club (%s)' % self.archer.club

    def save(self):
        with transaction.atomic():
            club = self.cleaned_data['club'] or self.archer.club
            entry = CompetitionEntry.objects.create(
                competition=self.competition,
                archer=self.archer,
                club=club,
                bowstyle=self.archer.bowstyle,
            )
            if len(self.session_rounds) == 1:
                SessionEntry.objects.create(
                    session_round=self.session_rounds[0],
                    competition_entry=entry
                )
            else:
                for session_round in self.cleaned_data['sessions']:
                    SessionEntry.objects.create(
                        session_round=session_round,
                        competition_entry=entry
                    )
