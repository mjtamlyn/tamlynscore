from django import forms

from core.models import Archer
from .models import CompetitionEntry, SessionRound, SessionEntry


class ArcherSearchForm(forms.Form):
    query = forms.CharField()

    def get_archers(self):
        # One day, do this with expressions and/or contrib.postgres. Please.
        term = self.cleaned_data['query']
        return Archer.objects.extra(
            select={'similarity': 'similarity("core_archer"."name", %s)'},
            select_params=[term],
            where=['"core_archer"."name" %% %s'],
            params=[term],
            order_by=['-similarity'],
        )


class EntryCreateForm(forms.Form):
    def __init__(self, archer, competition, **kwargs):
        super(EntryCreateForm, self).__init__(**kwargs)
        self.archer = archer
        self.competition = competition
        self.session_rounds = SessionRound.objects.filter(session__competition=competition)

    def save(self):
        entry = CompetitionEntry.objects.create(
            competition=self.competition,
            archer=self.archer,
            club=self.archer.club,
            bowstyle=self.archer.bowstyle,
        )
        if len(self.session_rounds) == 1:
            SessionEntry.objects.create(
                session_round=self.session_rounds[0],
                competition_entry=entry
            )
