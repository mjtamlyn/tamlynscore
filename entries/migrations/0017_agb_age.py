# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0016_auto_20151101_2157'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='has_agb_age_groups',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='competitionentry',
            name='agb_age',
            field=models.CharField(choices=[('', 'Senior'), ('U18', 'U18'), ('U16', 'U16'), ('U14', 'U14'), ('U12', 'U12')], max_length=3, blank=True, default=''),
        ),
    ]
