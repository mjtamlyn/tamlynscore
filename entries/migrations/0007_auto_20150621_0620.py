# -*- coding: utf-8 -*-

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0006_auto_20150612_2307'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='has_wa_age_groups',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='competitionentry',
            name='wa_age',
            field=models.CharField(default='', max_length=1, choices=[('C', 'Cadet'), ('J', 'Junior'), ('', 'Senior'), ('M', 'Master')]),
        ),
    ]
