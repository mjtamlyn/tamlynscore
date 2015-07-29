from django import forms

from .models import Archer


class ArcherForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ArcherForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'autofocus': ''})

    class Meta:
        model = Archer
        fields = '__all__'
