# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0010_auto_20150911_0924'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='competition',
            name='has_teams',
        ),
    ]
