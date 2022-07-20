# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0015_competition_admins'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competition',
            name='admins',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='resultsmode',
            name='mode',
            field=models.CharField(choices=[('all-shot', 'By round (include later shoots)'), ('by-round', 'By round'), ('by-round-progressional', 'By round (progressional)'), ('by-session', 'By session'), ('double-round', 'Double round'), ('seedings', 'Seedings'), ('team', 'Teams'), ('weekend', 'Weekend (Masters style)')], max_length=31),
        ),
    ]
