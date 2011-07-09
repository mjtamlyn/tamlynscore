from django import forms

from core.models import Club, Archer, GENDER_CHOICES
from entries.models import CompetitionEntry

GENDER_CHOICES = (('', '--------'),) + GENDER_CHOICES

class JsonChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.json()

class NewEntryForm(forms.ModelForm):

    archer_name = forms.CharField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Add an archer...'}))
    archer = JsonChoiceField(queryset=Archer.objects, required=False)

    club_name = forms.CharField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Club'}))
    club = JsonChoiceField(queryset=Club.objects, required=False)

    gender = forms.ChoiceField(choices=GENDER_CHOICES)

    class Meta:
        model = CompetitionEntry
