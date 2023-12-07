from django import forms

from .models import Archer, Bowstyle


class ArcherForm(forms.ModelForm):
    def __init__(self, competition=None, *args, **kwargs):
        super(ArcherForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'autofocus': ''})
        self.fields['bowstyle'].queryset = Bowstyle.objects.filter(ifaa_only=False)

        if competition:
            if competition.ifaa_rules:
                self.fields['bowstyle'].queryset = Bowstyle.objects.filter(ifaa_only=True)
                self.fields.pop('age')
                self.fields.pop('novice')
                self.fields.pop('club')
                self.fields.pop('agb_number')

        if self.initial:
            for name in self.initial:
                if name not in self.fields:
                    continue
                choices = getattr(self.fields[name], 'choices', None)
                if choices:
                    for item in choices:
                        if hasattr(item[1], 'value'):
                            value = item[1].value.lower()
                        else:
                            value = item[1].lower()
                        if value == str(self.initial[name]).lower():
                            self.initial[name] = item[0]

    class Meta:
        model = Archer
        fields = ['name', 'gender', 'club', 'bowstyle', 'age', 'novice', 'agb_number']


class ClubArcherForm(ArcherForm):
    def __init__(self, club, **kwargs):
        super(ClubArcherForm, self).__init__(**kwargs)
        self.club = club

    class Meta(ArcherForm.Meta):
        fields = ['name', 'gender', 'bowstyle', 'age', 'novice', 'agb_number']

    def save(self):
        self.instance.club = self.club
        return super(ClubArcherForm, self).save()
