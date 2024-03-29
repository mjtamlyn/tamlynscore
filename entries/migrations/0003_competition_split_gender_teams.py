# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0002_auto_20150128_0925'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='split_gender_teams',
            field=models.BooleanField(default=False, help_text='Does not affect novice teams'),
            preserve_default=True,
        ),
    ]
