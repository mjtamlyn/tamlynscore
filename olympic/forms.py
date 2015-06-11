from django import forms

from .models import Result


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

    def __init__(self, session_rounds, **kwargs):
        self.session_rounds = session_rounds
        super(SetupForm, self).__init__(**kwargs)
        for sr in self.session_rounds:
            self.fields['sr-%s-start' % sr.pk] = forms.IntegerField(label='Start target')
            self.fields['sr-%s-timing' % sr.pk] = forms.IntegerField(label='Pass')
            self.fields['sr-%s-spread' % sr.pk] = forms.ChoiceField(label='Target spread', choices=self.SPREAD_CHOICES)
