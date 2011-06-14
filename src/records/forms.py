from django import forms

from records.models import *

class ShootForm(forms.ModelForm):

    class Meta:
        model = Shoot
        exclude = ['competition']

