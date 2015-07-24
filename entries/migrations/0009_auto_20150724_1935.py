# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20150724_1935'),
        ('entries', '0008_auto_20150630_0830'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='use_county_teams',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='competitionentry',
            name='county',
            field=models.ForeignKey(to='core.County', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='competition',
            name='exclude_later_shoots',
            field=models.BooleanField(default=False, help_text='Only the first session can count for results'),
        ),
        migrations.AlterField(
            model_name='competition',
            name='split_gender_teams',
            field=models.BooleanField(default=False, help_text='Does not affect novice teams'),
        ),
        migrations.AlterField(
            model_name='competition',
            name='strict_b_teams',
            field=models.BooleanField(default=False, help_text='e.g. BUTC'),
        ),
        migrations.AlterField(
            model_name='competition',
            name='strict_c_teams',
            field=models.BooleanField(default=False, help_text='e.g. BUTC'),
        ),
        migrations.AlterField(
            model_name='competitionentry',
            name='age',
            field=models.CharField(default='S', choices=[('J', 'Junior'), ('S', 'Senior')], max_length=1),
        ),
        migrations.AlterField(
            model_name='competitionentry',
            name='club',
            field=models.ForeignKey(to='core.Club', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='competitionentry',
            name='novice',
            field=models.CharField(default='E', choices=[('N', 'Novice'), ('E', 'Experienced')], max_length=1),
        ),
        migrations.AlterField(
            model_name='competitionentry',
            name='wa_age',
            field=models.CharField(default='', blank=True, max_length=1, choices=[('C', 'Cadet'), ('J', 'Junior'), ('', 'Senior'), ('M', 'Master')]),
        ),
        migrations.AlterField(
            model_name='resultsmode',
            name='json',
            field=models.TextField(default='', blank=True),
        ),
        migrations.AlterField(
            model_name='resultsmode',
            name='mode',
            field=models.CharField(choices=[('weekend', 'Weekend (Masters style)'), ('by-round', 'By round'), ('seedings', 'Seedings'), ('team', 'Teams'), ('by-session', 'By session'), ('double-round', 'Double round'), ('by-round-progressional', 'By round (progressional)')], max_length=31),
        ),
        migrations.AlterField(
            model_name='session',
            name='scoring_system',
            field=models.CharField(choices=[('F', 'Full running slips'), ('D', 'Dozen running slips'), ('T', 'Totals only')], max_length=1),
        ),
        migrations.AlterField(
            model_name='sponsor',
            name='logo',
            field=models.ImageField(upload_to='sponsors'),
        ),
    ]
