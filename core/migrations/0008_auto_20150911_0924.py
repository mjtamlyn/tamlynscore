# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20150724_1945'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='county',
            options={'ordering': ('short_name',), 'verbose_name_plural': 'counties'},
        ),
        migrations.AddField(
            model_name='archer',
            name='archived',
            field=models.BooleanField(default=False),
        ),
    ]
