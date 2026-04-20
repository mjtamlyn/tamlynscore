from django import forms

from .models import Result, Seeding


class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        exclude = ('match', 'seed')


class SetsMatchForm(forms.Form):
    SCORE_CHOICES = {
        'Not started': {
            '0-0': '0-0',
        },
        'Set 1': {
            '2-0': '2-0',
            '1-1': '1-1',
            '0-2': '0-2',
        },
        'Set 2': {
            '4-0': '4-0',
            '3-1': '3-1',
            '2-2': '2-2',
            '1-3': '1-3',
            '0-4': '0-4',
        },
        'Set 3': {
            '6-0': '6-0',
            '5-1': '5-1',
            '4-2': '4-2',
            '3-3': '3-3',
            '2-4': '2-4',
            '1-5': '1-5',
            '0-6': '0-6',
        },
        'Set 4': {
            '7-1': '7-1',
            '6-2': '6-2',
            '5-3': '5-3',
            '4-4': '4-4',
            '3-5': '3-5',
            '2-6': '2-6',
            '1-7': '1-7',
        },
        'Set 5': {
            '7-3': '7-3',
            '6-4': '6-4',
            '5-5': '5-5',
            '4-6': '4-6',
            '3-7': '3-7',
        },
        'S/O': {
            '6-5': '6-5',
            '5-6': '5-6',
        },
    }
    score = forms.ChoiceField(choices=SCORE_CHOICES, widget=forms.RadioSelect(attrs={'class': 'match-sets'}), required=True)

    def __init__(self, instance, initial=None, **kwargs):
        self.match = instance
        if len(getattr(self.match, 'results', [])) == 2:
            initial = {'score': '%s-%s' % (self.match.score_1, self.match.score_2)}
        super().__init__(initial=initial, **kwargs)

    def save(self):
        score_1, score_2 = map(int, self.cleaned_data['score'].split('-'))
        self.update_score(self.match, self.match.seed_1, score_1)
        self.update_score(self.match, self.match.seed_2, score_2)

    def update_score(self, match, seed, score):
        seeding = Seeding.objects.get(session_round=match.session_round, seed=seed)
        try:
            instance = Result.objects.get(match=match, seed=seeding)
        except Result.DoesNotExist:
            instance = Result(match=match, seed=seeding)
        instance.total = score
        if instance.total >= 6:
            instance.win = True
        instance.save()


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
