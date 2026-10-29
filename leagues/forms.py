from django import forms

from .models import Leg


class LegCreateForm(forms.ModelForm):
    class Meta:
        model = Leg
        fields = ['index']
