from django import forms

from .models import Result, SessionRound


class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        exclude = ('match', 'seed')


class SetupForm(forms.Form):
    SPREAD_CHOICES = (
        ('', 'No special options'),
        ('expanded', 'One target per archer'),
        ('half', 'Only allocate half of the matches'),
        ('quarter', 'Only allocate 1/4 of the matches'),
        ('three-quarter', 'Only allocate 3/4 of the matches'),
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
    session_round = forms.ModelChoiceField(SessionRound)
    start = forms.IntegerField(label='Start target')
    level = forms.TypedChoiceField(coerce=int, choices=LEVEL_CHOICES)
    timing = forms.TypedChoiceField(label='Pass', coerce=int, choices=TIMING_CHOICES)
    spread = forms.ChoiceField(label='Target spread', choices=SPREAD_CHOICES, required=False)
    delete = forms.BooleanField(required=False)

    def __init__(self, session_rounds, **kwargs):
        self.session_rounds = session_rounds
        super(SetupForm, self).__init__(**kwargs)
        self.fields['session_round'].queryset = session_rounds

    def save(self):
        sr = self.cleaned_data['session_round']
        kwargs = {
            'level': self.cleaned_data['level'],
            'start': self.cleaned_data['start'],
            'timing': self.cleaned_data['timing'],
        }
        if self.cleaned_data['spread'] == 'expanded':
            kwargs['expanded'] = True
        if self.cleaned_data['spread'] == 'half':
            kwargs['half_only'] = True
        if self.cleaned_data['spread'] == 'quarter':
            kwargs['quarter_only'] = True
        if self.cleaned_data['spread'] == 'three-quarter':
            kwargs['three_quarters'] = True
        if self.cleaned_data['delete']:
            sr.remove_matches(self.cleaned_data['level'])
        else:
            sr.make_matches(**kwargs)
