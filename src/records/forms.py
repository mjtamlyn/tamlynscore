from django import forms

from records.models import *

class SmartSearchField(forms.ComboField):
    fields = [forms.Field, forms.ChoiceField]

class ShootForm(forms.ModelForm):

    competition = forms.models.ModelChoiceField(Competition.objects.all(), widget=forms.widgets.HiddenInput)
    archer = SmartSearchField()
    club = SmartSearchField()
    bowstyle = forms.models.ModelChoiceField(Bowstyle.objects.all(), widget=forms.widgets.RadioSelect(), initial=1)

    class Meta:
        model = Shoot

