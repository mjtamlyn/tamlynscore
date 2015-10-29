# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0013_host_club_null'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resultsmode',
            name='mode',
            field=models.CharField(max_length=31, choices=[('by-round', 'By round'), ('by-round-progressional', 'By round (progressional)'), ('by-session', 'By session'), ('double-round', 'Double round'), ('seedings', 'Seedings'), ('team', 'Teams'), ('weekend', 'Weekend (Masters style)')]),
        ),
    ]
