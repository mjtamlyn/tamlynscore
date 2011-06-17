from django import forms

from records.models import *

class ArcherField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.json()

class ScoreEntryForm(forms.ModelForm):

    archer = ArcherField(queryset=Archer.objects)

    class Meta:
        model = Entry
        exclude = ['competition']

