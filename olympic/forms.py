from django import forms

from .models import Result


class ResultForm(forms.ModelForm):
    shoot_off = forms.CharField(required=False)
    closest = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            arrows = self.instance.matcharrow_set.order_by('arrow_of_round')
            for arrow in arrows:
                if arrow.arrow_of_round <= 15:
                    self.initial['arrow_%s' % arrow.arrow_of_round] = str(arrow)
                elif arrow.arrow_of_round == 16:
                    self.initial['shoot_off'] = str(arrow)
                    self.initial['closest'] = arrow.closest
        for i in range(1, 16):
            self.fields['arrow_%s' % i] = forms.CharField(required=False)

    class Meta:
        model = Result
        fields = ('dns', 'win_by_forfeit')

    def arrow_value_check(self, arrow_value):
        data = {}
        if arrow_value == 'X':
            data['arrow_value'] = 10
            data['is_x'] = True
        elif arrow_value == 'M':
            data['arrow_value'] = 0
            data['is_x'] = False
        elif arrow_value:
            data['arrow_value'] = arrow_value
            data['is_x'] = False
        return data

    def clean(self):
        self.cleaned_data['shoot_off'] = self.arrow_value_check(self.cleaned_data.get('shoot_off'))
        for i in range(1, 16):
            self.cleaned_data['arrow_%s' % i] = self.arrow_value_check(self.cleaned_data.get('arrow_%s' % i))

    def save(self):
        if self.cleaned_data['arrow_1'] or self.cleaned_data['dns'] or self.cleaned_data['win_by_forfeit']:
            self.instance.total = 0
            super().save()
            for i in range(1, 16):
                data = self.cleaned_data['arrow_%s' % i]
                if data:
                    self.instance.matcharrow_set.update_or_create(
                        defaults=data,
                        arrow_of_round=i,
                    )
                else:
                    self.instance.matcharrow_set.filter(arrow_of_round=i).delete()
                if self.cleaned_data['shoot_off']:
                    self.instance.matcharrow_set.update_or_create(
                        defaults={
                            'closest': self.cleaned_data['closest'],
                            **self.cleaned_data['shoot_off'],
                        },
                        arrow_of_round=16,
                    )
            self.instance.match.update_totals()
        elif self.instance.pk:
            self.instance.delete()


class SetupForm(forms.Form):
    SPREAD_CHOICES = (
        ('', 'No special options'),
        ('expanded', 'One target per archer'),
    )
    MATCH_CHOICES = (
        ('', 'All matches'),
        ('half', 'Only allocate half of the matches'),
        ('quarter', 'Only allocate 1/4 of the matches'),
        ('eighth', 'Only allocate 1/8 of the matches'),
        ('three-quarter', 'Only allocate 3/4 of the matches'),
        ('first-half', 'Only allocate first half of the matches / Final only'),
        ('second-half', 'Only allocate second half of the matches / Bronze only'),
        ('full-ranked', 'Create all matches for a fully ranked H2H'),
    )
    LEVEL_CHOICES = (
        (1, 'Finals'),
        (2, 'Semis'),
        (3, 'Quarters'),
        (4, '1/8'),
        (5, '1/16'),
        (6, '1/32'),
        (7, '1/64'),
        (8, '1/128'),
    )
    TIMING_CHOICES = (
        (1, 'Pass A'),
        (2, 'Pass B'),
        (3, 'Pass C'),
        (4, 'Pass D'),
        (5, 'Pass E'),
        (6, 'Pass F'),
        (7, 'Pass G'),
        (8, 'Pass H'),
        (9, 'Pass I'),
        (10, 'Pass J'),
    )
    session_round = forms.ChoiceField()
    start = forms.IntegerField(label='Start target')
    level = forms.TypedChoiceField(coerce=int, choices=LEVEL_CHOICES)
    timing = forms.TypedChoiceField(label='Pass', coerce=int, choices=TIMING_CHOICES)
    spread = forms.ChoiceField(label='Target spread', choices=SPREAD_CHOICES, required=False)
    matches = forms.ChoiceField(label='Matches', choices=MATCH_CHOICES, required=False)
    delete = forms.BooleanField(required=False)

    def __init__(self, session_rounds, **kwargs):
        super(SetupForm, self).__init__(**kwargs)
        self.fields['session_round'].choices = [(None, '-----------')] + [(session_round.id, session_round.category.name) for session_round in session_rounds]
        self.sr_lookup = {sr.id: sr for sr in session_rounds}

    def save(self):
        sr = self.sr_lookup[int(self.cleaned_data['session_round'])]
        kwargs = {
            'level': self.cleaned_data['level'],
            'start': self.cleaned_data['start'],
            'timing': self.cleaned_data['timing'],
        }
        if sr.shot_round.team_type:
            kwargs['expanded'] = True
        if self.cleaned_data['spread'] == 'expanded':
            kwargs['expanded'] = True
        if self.cleaned_data['matches'] == 'half':
            kwargs['half_only'] = True
        if self.cleaned_data['matches'] == 'quarter':
            kwargs['quarter_only'] = True
        if self.cleaned_data['matches'] == 'eighth':
            kwargs['eighth_only'] = True
        if self.cleaned_data['matches'] == 'three-quarter':
            kwargs['three_quarters'] = True
        if self.cleaned_data['matches'] == 'first-half':
            kwargs['first_half_only'] = True
        if self.cleaned_data['matches'] == 'second-half':
            kwargs['second_half_only'] = True
        if self.cleaned_data['matches'] == 'full-ranked':
            kwargs['full_ranked'] = True
        if self.cleaned_data['delete']:
            sr.remove_matches(self.cleaned_data['level'])
        else:
            sr.make_matches(**kwargs)
