# -*- coding: utf-8 -*-

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0003_competition_split_gender_teams'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='session',
            options={'ordering': ['start']},
        ),
    ]
