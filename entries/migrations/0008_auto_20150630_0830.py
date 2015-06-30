# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0007_auto_20150621_0620'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competitionentry',
            name='wa_age',
            field=models.CharField(default=b'', max_length=1, blank=True, choices=[(b'C', b'Cadet'), (b'J', b'Junior'), (b'', b'Senior'), (b'M', b'Master')]),
        ),
    ]
