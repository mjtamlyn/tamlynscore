from django import forms

from scores.models import Arrow, Score

class ArrowForm(forms.ModelForm):

    arrow_value = forms.CharField(required=False)

    def clean(self):
        arrow_value = self.cleaned_data.get('arrow_value', 'M')
        if arrow_value == 'X':
            self.cleaned_data['arrow_value'] = 10
            self.cleaned_data['is_x'] = True
        else:
            self.cleaned_data['is_x'] = False
        if arrow_value == 'M' or arrow_value == '':
            self.cleaned_data['arrow_value'] = 0
        return self.cleaned_data

    class Meta:
        model = Arrow
        exclude = ['score', 'arrow_of_round']

def get_arrow_formset(scores, session_round, boss, dozen, arrows_per_end, data=None):
    forms_list = []
    for score in scores:
        target = {
                'forms': [],
                'archer': score.target.session_entry.competition_entry.archer,
                'target': score.target.target,
                'running_total': score.running_total(dozen),
        }
        for arrow in range(1, arrows_per_end + 1):
            prefix = score.target.target + str(arrow)
            try:
                instance = Arrow.objects.get(score=score, arrow_of_round=int(dozen)*arrows_per_end + arrow)
            except Arrow.DoesNotExist:
                instance = Arrow(score=score, arrow_of_round=int(dozen)*arrows_per_end + arrow)
            target['forms'].append(ArrowForm(data, instance=instance, prefix=prefix))
        forms_list.append(target)
    return forms_list
