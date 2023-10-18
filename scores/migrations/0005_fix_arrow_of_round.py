# Generated by Django 4.2.6 on 2023-10-18 09:45

from django.db import migrations


def update_arrow_of_round(apps, schema):
    Arrow = apps.get_model('scores', 'Arrow')
    arrows = Arrow.objects.select_related('score__target__session_entry__session_round__session').order_by('score_id', 'arrow_of_round')
    for a in arrows.iterator():
        session = a.score.target.session_entry.session_round.session
        a.arrow_of_round = a.arrow_of_round - session.arrows_entered_per_end
        a.save()


class Migration(migrations.Migration):

    dependencies = [
        ('scores', '0004_score_is_actual_zero'),
        ('entries', '0037_entry_users'),
    ]

    operations = [
        migrations.RunPython(update_arrow_of_round, migrations.RunPython.noop),
    ]
