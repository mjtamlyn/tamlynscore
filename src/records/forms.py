from django import forms

from records.models import *

class ArcherField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.json()

class ScoreEntryForm(forms.ModelForm):

    archer_name = forms.CharField()
    archer = ArcherField(queryset=Archer.objects, required=False)
    new_archer = forms.BooleanField(required=False)
    gender = forms.ChoiceField(required=False, choices=GENDER_CHOICES)

    def clean(self):
        if self.cleaned_data['new_archer']:
            try:
                archer = Archer.objects.get(name=self.cleaned_data['archer_name'], club=self.cleaned_data['club'])
            except Archer.DoesNotExist:
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


class ClubForm(forms.ModelForm):
    class Meta:
        model = Club

class ArrowForm(forms.ModelForm):
    class Meta:
        model = Arrow
        exclude = ['subround', 'entry', 'arrow_of_round']

def get_arrow_formset(the_round, target_no, doz_no):
    archers = Entry.objects.filter(shot_round=the_round, target__startswith=target_no).order_by('target')
    forms_list = []
    for archer in archers:
        target = {
                'forms': [],
                'archer': archer.archer,
                'target': archer.target,
        }
        for arrow in range(1, 13):
            prefix = archer.target[-1] + str(arrow)
            target['forms'].append(ArrowForm(prefix=prefix))
        forms_list.append(target)
    return forms_list
