from django import forms
from django.db.models import Count
from django.utils.safestring import mark_safe

from core.models import Club, Archer, GENDER_CHOICES
from entries.models import CompetitionEntry

GENDER_CHOICES = (('', ''),) + GENDER_CHOICES

class ButtonWidget(forms.widgets.Select):
    def render(self, name, value, attrs=None):
        response = u"""<div class="buttons-widget" id="{name}-widget">
                        <div class="select">
                            {select}
                        </div>
                        """
        for choice in self.choices:
            if choice[0]:
                response += u"""<div class="button" rel="{0}">
                                {1}
                            </div>""".format(*choice)
        response += u'</div>'
        select = super(ButtonWidget, self).render(name, value, attrs=attrs)
        response = response.format(name=name, select=select)
        return mark_safe(response)

class JsonChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.json()

class SessionChoiceField(forms.ModelChoiceField):
    widget = ButtonWidget

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

        gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=ButtonWidget)
        gnas_no = forms.CharField(widget=forms.widgets.TextInput(attrs={'placeholder': 'GNAS number'}))

        class Meta:
            model = CompetitionEntry
            widgets = {
                'bowstyle': ButtonWidget,
                'novice': ButtonWidget,
                'age': ButtonWidget,
            }

        def __init__(self, *args, **kwargs):
            super(NewEntryForm, self).__init__(*args, **kwargs)
            sessions = competition.session_set.annotate(count=Count('sessionround')).filter(count__gt=0).order_by('start')
            for i in range(len(sessions)):
                session = sessions[i]
                self.fields['session-{0}'.format(i)] = SessionChoiceField(sessions[i])

        def sessions(self):
            response = u''
            for field in self.fields:
                if 'session' in field:
                    response += unicode(self[field])
            return mark_safe(response)


    return NewEntryForm
