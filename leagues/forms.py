import datetime

from django import forms
from django.db import transaction

from core.models import User
from entries.models import SCORING_ARCHER, Competition, Tournament
from scores.result_modes import ByRound, Team

from .models import ConfigTemplate, Leg


class LegFields(forms.ModelForm):
    name = forms.CharField(help_text='Human readable name, e.g. "MyLeague 1999-2000 Leg 1"')
    slug = forms.SlugField(label="URL segment", help_text='Used in urls. Historically just the leg number, e.g. "1". Must be unique by season.')

    class Meta:
        model = Leg
        fields = ['name', 'slug']


class LegCreateForm(LegFields):
    config_template = forms.ModelChoiceField(
        ConfigTemplate.objects,
        label="Competition configuration",
        help_text="Default configuration for the leg results, and events within the leg.",
    )

    def __init__(self, league, season, *args, **kwargs):
        self.league = league
        self.season = season

        super().__init__(*args, **kwargs)

        self.fields['name'].widget.attrs['placeholder'] = str(self.season) + " Leg …"
        self.fields['config_template'].queryset = self.league.configtemplate_set.order_by('-id')

    @transaction.atomic
    def save(self):
        self.instance.season = self.season

        for field in ConfigTemplate._meta.fields:
            if field.name in ['id', 'league', 'name']:
                continue
            setattr(
                self.instance,
                field.name,
                getattr(self.cleaned_data['config_template'], field.name),
            )

        instance = super().save()

        instance.result_modes.create(mode=ByRound.slug)
        instance.result_modes.create(mode=Team.slug)

        return instance


class LegUpdateForm(LegFields):
    pass


class EventCompetitionForm(forms.ModelForm):
    leg = forms.ModelChoiceField(
        Leg.objects,
        required=False,
        help_text='Attach to a leg to get combined results across venues',
    )
    config_template = forms.ModelChoiceField(
        ConfigTemplate.objects,
        required=False,
        label="Competition configuration",
        help_text="Provide only if not attaching to a leg",
    )
    tournament = forms.ModelChoiceField(
        Tournament.objects,
        label='Event name',
        help_text='Determines which previous editions to link this event to',
    )
    admins = forms.ModelMultipleChoiceField(
        User.objects,
        label='Event Administrators',
        help_text='Hold ctrl or cmd to select multiple',
    )
    session_1 = forms.TimeField(
        label='Session 1 time',
        help_text=(
            '''At this point, every session defaults to Portsmouths only.
            Configuration defaults to 4 archers per target and on-device
            scoring. Better flexibility coming soon?'''
        ),
    )
    session_2 = forms.TimeField(label='Session 2 time', help_text='Optional', required=False)
    session_3 = forms.TimeField(label='Session 3 time', help_text='Optional', required=False)

    class Meta:
        model = Competition
        fields = ['leg', 'config_template', 'tournament', 'date', 'session_1', 'session_2', 'session_3']

    def clean(self):
        if self.cleaned_data['leg'] and self.cleaned_data['config_template']:
            raise forms.ValidationError('Please choose either a leg or a config template, but not both.')
        if not self.cleaned_data['leg'] and not self.cleaned_data['config_template']:
            raise forms.ValidationError('Please choose either a leg or a config template, but not both.')

    def __init__(self, league, season, *args, **kwargs):
        self.league = league
        self.season = season

        super().__init__(*args, **kwargs)

        self.fields['leg'].queryset = self.season.leg_set.all()
        self.fields['config_template'].queryset = self.league.configtemplate_set.order_by('-id')
        self.fields['tournament'].queryset = self.league.tournaments.order_by('full_name')
        self.fields['admins'].queryset = self.league.managed_accounts.order_by('name')

        self.fields['date'].widget.input_type = 'date'
        self.fields['session_1'].widget.input_type = 'time'
        self.fields['session_2'].widget.input_type = 'time'
        self.fields['session_3'].widget.input_type = 'time'

    @transaction.atomic
    def save(self):
        if self.cleaned_data['leg']:
            for field in ConfigTemplate._meta.fields:
                if field.name in ['id', 'league', 'name']:
                    continue
                setattr(
                    self.instance,
                    field.name,
                    getattr(self.cleaned_data['leg'], field.name),
                )
        else:
            for field in ConfigTemplate._meta.fields:
                if field.name in ['id', 'league', 'name']:
                    continue
                setattr(
                    self.instance,
                    field.name,
                    getattr(self.cleaned_data['config_template'], field.name),
                )

        instance = super().save()

        # TODO: this is hacky!
        from core.models import Round
        portsmouth = Round.objects.get(name='Portsmouth')
        session = instance.session_set.create(
            start=datetime.datetime.combine(instance.date, self.cleaned_data['session_1']),
            scoring_system=SCORING_ARCHER,
            archers_per_target=4,
            arrows_entered_per_end=3,
        )
        session.sessionround_set.create(shot_round=portsmouth)
        if self.cleaned_data['session_2']:
            session = instance.session_set.create(
                start=datetime.datetime.combine(instance.date, self.cleaned_data['session_2']),
                scoring_system=SCORING_ARCHER,
                archers_per_target=4,
                arrows_entered_per_end=3,
            )
            session.sessionround_set.create(shot_round=portsmouth)
        if self.cleaned_data['session_3']:
            session = instance.session_set.create(
                start=datetime.datetime.combine(instance.date, self.cleaned_data['session_3']),
                scoring_system=SCORING_ARCHER,
                archers_per_target=4,
                arrows_entered_per_end=3,
            )
            session.sessionround_set.create(shot_round=portsmouth)

        instance.result_modes.create(mode=ByRound.slug)
        instance.result_modes.create(mode=Team.slug)

        for organiser in self.league.organisers.all():
            instance.admins.add(organiser)
        for admin in self.cleaned_data['admins']:
            instance.admins.add(admin)

        if self.cleaned_data['leg']:
            self.cleaned_data['leg'].competitions.add(instance)
