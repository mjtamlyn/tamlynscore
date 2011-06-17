from django import forms

from records.models import *

class ArcherField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.json()

class ScoreEntryForm(forms.ModelForm):

    archer = ArcherField(queryset=Archer.objects)
    new_archer = forms.BooleanField()
    gender = forms.ChoiceField(required=False, choices=GENDER_CHOICES)

    class Meta:
        model = Entry
        exclude = ['competition']

