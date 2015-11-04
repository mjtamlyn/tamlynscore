from django import forms

from .models import Archer


class ArcherForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ArcherForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'autofocus': ''})

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
