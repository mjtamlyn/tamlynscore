# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0009_auto_20150724_1935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resultsmode',
            name='mode',
            field=models.CharField(max_length=31, choices=[('by-round', 'By round'), ('weekend', 'Weekend (Masters style)'), ('seedings', 'Seedings'), ('by-session', 'By session'), ('team', 'Teams'), ('double-round', 'Double round'), ('by-round-progressional', 'By round (progressional)')]),
        ),
    ]
