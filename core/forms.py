import floppyforms.__future__ as forms

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
