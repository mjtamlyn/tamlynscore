# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def nullify_novice_team_size(apps, editor):
    Competition = apps.get_model('entries', 'Competition')
    Competition.objects.filter(has_novices=False).update(novice_team_size=None)


def default_novice_team_size(apps, editor):
    Competition = apps.get_model('entries', 'Competition')
    Competition.objects.filter(novice_team_size=None).update(novice_team_size=3)


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0011_auto_20151004_1621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competition',
            name='novice_team_size',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.RunPython(
            nullify_novice_team_size,
            default_novice_team_size,
        ),
    ]
