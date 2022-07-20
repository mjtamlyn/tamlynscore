# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='season',
            options={'ordering': ('-start_date',)},
        ),
        migrations.AddField(
            model_name='league',
            name='slug',
            field=models.SlugField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='season',
            name='end_date',
            field=models.DateField(default=datetime.date(2015, 12, 7)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='season',
            name='slug',
            field=models.SlugField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='season',
            name='start_date',
            field=models.DateField(default=datetime.date(2015, 12, 7)),
            preserve_default=False,
        ),
    ]
