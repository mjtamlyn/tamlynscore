# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20150724_1935'),
    ]

    operations = [
        migrations.AddField(
            model_name='county',
            name='short_name',
            field=models.CharField(max_length=50, unique=True, default='Oxfordshire'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='county',
            name='name',
            field=models.CharField(max_length=500, unique=True),
        ),
    ]
