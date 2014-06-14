from django.db import transaction
from django.db.models import Q
from django import forms

from core.models import Archer, Bowstyle, Club, AGE_CHOICES, NOVICE_CHOICES
from .models import CompetitionEntry, SessionEntry


NULL_AGE_CHOICES = (('', '---------'),) + AGE_CHOICES
NULL_NOVICE_CHOICES = (('', '---------'),) + NOVICE_CHOICES


class SearchWidget(forms.TextInput):
    input_type = 'search'


class SessionChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return unicode(obj.shot_round)


class ArcherSearchForm(forms.Form):
    query = forms.CharField(widget=SearchWidget(attrs={'placeholder': 'Search', 'autofocus': True}))

    def get_qs(self):
        return Archer.objects.filter(
            (Q(name__icontains=self.cleaned_data['query']) |
                Q(club__name__icontains=self.cleaned_data['query']))
        )


class EntryCreateForm(forms.Form):
    archer = forms.ModelChoiceField(Archer.objects)
    bowstyle = forms.ModelChoiceField(Bowstyle.objects)
    club = forms.ModelChoiceField(Club.objects)
    age = forms.ChoiceField(choices=NULL_AGE_CHOICES, required=False)
    novice = forms.ChoiceField(choices=NULL_NOVICE_CHOICES, required=False)
    guest = forms.BooleanField(required=False)

    def __init__(self, competition, **kwargs):
        self.competition = competition
        super(EntryCreateForm, self).__init__(**kwargs)
        self.session_fields = []
        for session in self.competition.sessions_with_rounds():
            field = SessionChoiceField(session.sessionround_set.all(), required=False, label=session.start)
            field.key = 'session_%s' % session.pk
            self.fields[field.key] = field
            self.session_fields.append(field)

    def bound_session_fields(self):
        return [self[field.key] for field in self.session_fields]

    def clean(self):
        data = self.cleaned_data
        if 'archer' in data:
            archer = data['archer']
            for field in ['age', 'novice']:
                if field not in data:
                    self.cleaned_data[field] = getattr(archer, field)
        if self.session_fields:
            if not any(data[field.key] for field in self.session_fields):
                raise forms.ValidationError('Must enter at least one session')
        return self.cleaned_data

    def save(self):
        data = self.cleaned_data
        with transaction.atomic():
            competition_entry = CompetitionEntry.objects.create(
                competition=self.competition,
                archer=data['archer'],
                club=data['club'],
                bowstyle=data['bowstyle'],
                age=data['age'],
                novice=data['novice'],
                guest=data['guest'],
            )
            for field in self.session_fields:
                if data[field.key]:
                    SessionEntry.objects.create(
                        competition_entry=competition_entry,
                        session_round=data[field.key],
                    )
        return competition_entry
