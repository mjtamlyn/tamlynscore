# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-08-16 10:24
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0021_custom_team_names'),
        ('olympic', '0009_team_h2h'),
    ]

    operations = [
        migrations.AddField(
            model_name='seeding',
            name='entry_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='entries.CompetitionEntry'),
        ),
        migrations.AddField(
            model_name='seeding',
            name='entry_3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='entries.CompetitionEntry'),
        ),
    ]
