from django import forms

from core.models import Club, Archer, GENDER_CHOICES
from entries.models import CompetitionEntry

class JsonChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.json()

class NewEntryForm(forms.ModelForm):

    archer_name = forms.CharField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Add an archer...'}))
    archer = JsonChoiceField(queryset=Archer.objects, required=False)
    new_archer = forms.BooleanField(required=False)

    club_name = forms.CharField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Club'}))
    club = JsonChoiceField(queryset=Club.objects, required=False)
    new_club = forms.BooleanField(required=False)

    gender = forms.ChoiceField(required=False, choices=GENDER_CHOICES)

    class Meta:
        model = CompetitionEntry
