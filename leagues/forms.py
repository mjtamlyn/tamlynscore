from django import forms
from django.db import transaction

from scores.result_modes import ByRound, Team

from .models import ConfigTemplate, Leg


class LegCreateForm(forms.ModelForm):
    name = forms.CharField(help_text='Human readable name, e.g. "MyLeague 1999-2000 Leg 1"')
    slug = forms.SlugField(label="URL segment", help_text='Used in urls. Historically just the leg number, e.g. "1". Must be unique by season.')
    config_template = forms.ModelChoiceField(ConfigTemplate.objects, label="Competition configuration", help_text="Default configuration for the leg results, and events within the leg.")

    class Meta:
        model = Leg
        fields = ['name', 'slug']

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
