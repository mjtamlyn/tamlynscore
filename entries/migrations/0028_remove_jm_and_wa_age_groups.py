# Generated by Django 4.1.2 on 2023-02-03 11:30

from django.db import migrations
from django.db.models import F


def remove_jm_and_wa_age_groups(apps, schema_editor):
    Competition = apps.get_model('entries', 'Competition')
    CompetitionEntry = apps.get_model('entries', 'CompetitionEntry')

    # JM age groups first
    entries = CompetitionEntry.objects.filter(competition__has_junior_masters_age_groups=True)
    entries.update(agb_age=F('junior_masters_age'))
    Competition.objects.filter(has_junior_masters_age_groups=True).update(has_agb_age_groups=True)

    # WA age groups next - bit more complex as they had different DB reprs
    entries = CompetitionEntry.objects.filter(competition__has_wa_age_groups=True)
    entries.filter(wa_age='C').update(agb_age='U18')
    entries.filter(wa_age='J').update(agb_age='U21')
    entries.filter(wa_age='M').update(agb_age='50+')
    entries.filter(wa_age='N').update(agb_age='65+')
    Competition.objects.filter(has_wa_age_groups=True).update(has_agb_age_groups=True)


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0027_new_agb_age_groups'),
    ]

    operations = [
        migrations.RunPython(
            remove_jm_and_wa_age_groups,
            migrations.RunPython.noop,
        ),
    ]
