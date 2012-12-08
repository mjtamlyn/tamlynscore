from django import forms
from django.utils.safestring import mark_safe

from core.models import Club, Archer, GENDER_CHOICES
from entries.models import CompetitionEntry, SessionEntry

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

class SelectWidget(forms.widgets.MultiWidget):
    def __init__(self, attrs=None):
        widgets = [forms.widgets.Select(attrs=attrs), forms.widgets.TextInput(attrs=attrs)]
        super(SelectWidget, self).__init__(widgets, attrs)
        self.choices = []

    def decompress(self, value):
        return [value, value]

    def _get_choices(self):
        return self._choices
    def _set_choices(self, value):
        self.widgets[0].choices = value
        self._choices = value
    choices = property(_get_choices, _set_choices)

    def render(self, name, value, attrs=None):
        # Hacked from the default one to allow format_output to know about name
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized
        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)
        output = []
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        for i, widget in enumerate(self.widgets):
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None
            if id_:
                final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))
            output.append(widget.render(name + '_%s' % i, widget_value, final_attrs))
        return mark_safe(self.format_output(output, name))

    def format_output(self, rendered_widgets, name):
        output = u"""
                <div class="select-widget" id="{name}-widget">
                    <div class="select">
                        {0}
                    </div>
                    {1}
                    <div class="options-wrapper">
                        <ul class="options"></ul>
                    </div>
                </div>
        """.format(*rendered_widgets, name=name)
        return mark_safe(output)

class JsonChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.json()

    def to_python(self, value):
        pk, name = value
        if pk:
            return super(JsonChoiceField, self).to_python(pk)
        elif name:
            return self.queryset.model(name=name)

class SessionChoiceField(forms.ModelChoiceField):
    widget = ButtonWidget

    def __init__(self, session, *args, **kwargs):
        qs = session.sessionround_set.select_related('shot_round')
        super(SessionChoiceField, self).__init__(qs, *args, **kwargs)

    def label_from_instance(self, obj):
        return obj.shot_round

def new_entry_form_for_competition(competition):
    class NewEntryForm(forms.ModelForm):

        archer = JsonChoiceField(queryset=Archer.objects.select_related('bowstyle', 'club'), widget=SelectWidget(attrs={'placeholder': 'Add an archer...'}))
        club = JsonChoiceField(queryset=Club.objects, widget=SelectWidget(attrs={'placeholder': 'Club'}))

        gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=ButtonWidget)
        gnas_no = forms.IntegerField(widget=forms.widgets.TextInput(attrs={'placeholder': 'GNAS number'}), required=False)

        class Meta:
            model = CompetitionEntry
            exclude = ['competition', 'archer', 'club']
            widgets = {
                'bowstyle': ButtonWidget,
                'novice': ButtonWidget,
                'age': ButtonWidget,
            }

        def __init__(self, *args, **kwargs):
            super(NewEntryForm, self).__init__(*args, **kwargs)
            sessions = competition.sessions_with_rounds()
            self.session_fields = {}
            for i in range(len(sessions)):
                session = sessions[i]
                field = SessionChoiceField(sessions[i], required=False)
                self.fields['session-{0}'.format(i)] = field
                self.session_fields['session-{0}'.format(i)] = field

        def save(self, *args, **kwargs):
            #TODO: deal with commit=False
            club = self.cleaned_data['club']
            if not club.pk:
                club.short_name = club.name[:50]
                club.clean()
                club.save()
            archer = self.cleaned_data['archer']
            if not archer.pk:
                archer.club = club
                archer.bowstyle = self.cleaned_data['bowstyle']
                archer.novice = self.cleaned_data['novice']
                archer.gnas_no = self.cleaned_data['gnas_no']
                archer.age = self.cleaned_data['age']
                archer.gender = self.cleaned_data['gender']
                archer.save()
            entry = super(NewEntryForm, self).save(commit=False, *args, **kwargs)
            entry.archer = archer
            entry.club = club
            entry.save()
            for field in self.session_fields:
                if self.cleaned_data[field]:
                    session_round = self.cleaned_data[field]
                    session_entry = SessionEntry(competition_entry=entry, session_round=session_round)
                    session_entry.save()
            return entry

        def clean(self):
            sessions = filter(None, [self.cleaned_data[field] for field in self.session_fields])
            if not sessions:
                raise forms.ValidationError('You should enter at least one session')
            return self.cleaned_data

        def sessions(self):
            response = u''
            for field in self.session_fields:
                response += unicode(self[field])
            return mark_safe(response)


    return NewEntryForm
