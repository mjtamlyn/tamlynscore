# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0005_resultsmode_json'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resultsmode',
            name='json',
            field=models.TextField(default=b'', blank=True),
        ),
    ]
