from django import forms

from core.models import Archer, GENDER_CHOICES
from entries.models import CompetitionEntry

class ArcherField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.json()

class NewEntryForm(forms.ModelForm):

    archer_name = forms.CharField()
    archer = ArcherField(queryset=Archer.objects, required=False)
    new_archer = forms.BooleanField(required=False)
    gender = forms.ChoiceField(required=False, choices=GENDER_CHOICES)

    class Meta:
        model = CompetitionEntry
