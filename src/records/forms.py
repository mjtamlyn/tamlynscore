from django import forms

from records.models import *

class ArcherField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.json()

class ScoreEntryForm(forms.ModelForm):

    archer_name = forms.CharField()
    archer = ArcherField(queryset=Archer.objects)
    new_archer = forms.BooleanField(required=False)
    gender = forms.ChoiceField(required=False, choices=GENDER_CHOICES)

    def clean(self):
        if self.cleaned_data['new_archer']:
            params = {
                    'name': self.cleaned_data['archer_name'],
                    'bowstyle': self.cleaned_data['bowstyle'],
                    'club': self.cleaned_data['club'],
                    'gender': self.cleaned_data['gender'],
            }
            archer = Archer(**params)
            archer.save()
            self.cleaned_data['archer'] = archer
        return self.cleaned_data

    class Meta:
        model = Entry
        exclude = ['shot_round']

