# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150528_2034'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='club',
            name='abbreviation',
        ),
    ]
