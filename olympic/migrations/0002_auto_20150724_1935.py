# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('olympic', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='gender',
            field=models.CharField(blank=True, max_length=1, null=True, choices=[('G', 'Gent'), ('L', 'Lady')]),
        ),
        migrations.AlterField(
            model_name='olympicround',
            name='match_type',
            field=models.CharField(choices=[('T', 'Sets'), ('C', 'Score')], max_length=1),
        ),
    ]
