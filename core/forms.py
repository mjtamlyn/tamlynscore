from django import forms

from .models import Archer


class ArcherUpdateForm(forms.ModelForm):
    class Meta:
        model = Archer
        fields = ('club', 'gnas_no')
