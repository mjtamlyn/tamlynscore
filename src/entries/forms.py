from django import forms
from django.db.models import Count

from core.models import Club, Archer, GENDER_CHOICES
from entries.models import CompetitionEntry

GENDER_CHOICES = (('', ''),) + GENDER_CHOICES

class JsonChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.json()

class SessionChoiceField(forms.ModelChoiceField):
    def __init__(self, session, *args, **kwargs):
        qs = session.sessionround_set
        super(SessionChoiceField, self).__init__(qs, *args, **kwargs)

    def label_from_instance(self, obj):
        return obj.shot_round

def new_entry_form_for_competition(competition):
    class NewEntryForm(forms.ModelForm):

        archer_name = forms.CharField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Add an archer...'}))
        archer = JsonChoiceField(queryset=Archer.objects, required=False)

        club_name = forms.CharField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Club'}))
        club = JsonChoiceField(queryset=Club.objects, required=False)

        gender = forms.ChoiceField(choices=GENDER_CHOICES)
        gnas_no = forms.CharField(widget=forms.widgets.TextInput(attrs={'placeholder': 'GNAS number'}))

        class Meta:
            model = CompetitionEntry

        def __init__(self, *args, **kwargs):
            super(NewEntryForm, self).__init__(*args, **kwargs)
            sessions = competition.session_set.annotate(count=Count('sessionround')).filter(count__gt=0).order_by('start')
            for i in range(len(sessions)):
                session = sessions[i]
                self.fields['session-{0}'.format(i)] = SessionChoiceField(sessions[i])

    return NewEntryForm
