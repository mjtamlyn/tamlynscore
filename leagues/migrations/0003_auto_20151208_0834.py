# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0002_auto_20151207_1720'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResultsMode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('mode', models.CharField(choices=[('all-shot', 'By round (include later shoots)'), ('by-round', 'By round'), ('by-round-progressional', 'By round (progressional)'), ('by-session', 'By session'), ('double-round', 'Double round'), ('seedings', 'Seedings'), ('team', 'Teams'), ('weekend', 'Weekend (Masters style)')], max_length=31)),
                ('leaderboard_only', models.BooleanField(default=False)),
                ('leg', models.ForeignKey(to='leagues.Leg', related_name='result_modes')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='resultsmode',
            unique_together=set([('leg', 'mode')]),
        ),
    ]
