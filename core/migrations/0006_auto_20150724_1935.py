# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20150630_0830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archer',
            name='age',
            field=models.CharField(default='S', choices=[('J', 'Junior'), ('S', 'Senior')], max_length=1),
        ),
        migrations.AlterField(
            model_name='archer',
            name='club',
            field=models.ForeignKey(to='core.Club', blank=True, null=True, on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='archer',
            name='gender',
            field=models.CharField(choices=[('G', 'Gent'), ('L', 'Lady')], max_length=1),
        ),
        migrations.AlterField(
            model_name='archer',
            name='novice',
            field=models.CharField(default='E', choices=[('N', 'Novice'), ('E', 'Experienced')], max_length=1),
        ),
        migrations.AlterField(
            model_name='archer',
            name='wa_age',
            field=models.CharField(default='', blank=True, max_length=1, choices=[('C', 'Cadet'), ('J', 'Junior'), ('', 'Senior'), ('M', 'Master')]),
        ),
        migrations.AlterField(
            model_name='round',
            name='scoring_type',
            field=models.CharField(choices=[('F', 'Five Zone Imperial'), ('T', 'AGB Indoor - Ten Zone, no Xs, with hits'), ('X', 'WA Outdoor - Ten Zone, with Xs, no hits'), ('I', 'WA Indoor - Ten Zone, no Xs, no hits'), ('W', 'Worcester')], max_length=1),
        ),
        migrations.AlterField(
            model_name='subround',
            name='unit',
            field=models.CharField(choices=[('m', 'metres'), ('y', 'yards')], max_length=1),
        ),
    ]
