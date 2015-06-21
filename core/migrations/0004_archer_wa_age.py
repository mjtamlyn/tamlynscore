# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_club_abbreviation'),
    ]

    operations = [
        migrations.AddField(
            model_name='archer',
            name='wa_age',
            field=models.CharField(default=b'', max_length=1, choices=[(b'C', b'Cadet'), (b'J', b'Junior'), (b'', b'Senior'), (b'M', b'Master')]),
        ),
    ]
