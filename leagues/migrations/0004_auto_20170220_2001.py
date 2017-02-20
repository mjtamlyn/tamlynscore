# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-02-20 20:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0003_auto_20151208_0834'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='leg',
            name='clubs',
        ),
        migrations.RemoveField(
            model_name='resultsmode',
            name='leaderboard_only',
        ),
        migrations.RemoveField(
            model_name='season',
            name='clubs',
        ),
        migrations.AddField(
            model_name='leg',
            name='allow_incomplete_teams',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='leg',
            name='combine_rounds_for_team_scores',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='leg',
            name='compound_team_size',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='leg',
            name='exclude_later_shoots',
            field=models.BooleanField(default=False, help_text='Only the first session can count for results'),
        ),
        migrations.AddField(
            model_name='leg',
            name='force_mixed_teams',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='leg',
            name='force_mixed_teams_recurve_only',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='leg',
            name='has_agb_age_groups',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='leg',
            name='has_guests',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='leg',
            name='has_juniors',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='leg',
            name='has_novices',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='leg',
            name='has_wa_age_groups',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='leg',
            name='junior_team_size',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='leg',
            name='novice_team_size',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='leg',
            name='novices_in_experienced_individual',
            field=models.BooleanField(default=False, help_text='Puts the novices in experienced results and their own category'),
        ),
        migrations.AddField(
            model_name='leg',
            name='novices_in_experienced_teams',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='leg',
            name='split_gender_teams',
            field=models.BooleanField(default=False, help_text='Does not affect novice teams'),
        ),
        migrations.AddField(
            model_name='leg',
            name='strict_b_teams',
            field=models.BooleanField(default=False, help_text='e.g. BUTC'),
        ),
        migrations.AddField(
            model_name='leg',
            name='strict_c_teams',
            field=models.BooleanField(default=False, help_text='e.g. BUTC'),
        ),
        migrations.AddField(
            model_name='leg',
            name='team_size',
            field=models.PositiveIntegerField(default=4),
        ),
        migrations.AddField(
            model_name='leg',
            name='use_county_teams',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='leg',
            name='use_custom_teams',
            field=models.BooleanField(default=False),
        ),
    ]
