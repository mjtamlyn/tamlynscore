# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0001_initial'),
    ]

    operations = [
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
            name='start_date',
            field=models.DateField(default=datetime.date(2015, 12, 7)),
            preserve_default=False,
        ),
    ]
