# -*- coding: utf-8 -*-

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_archer_wa_age'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archer',
            name='wa_age',
            field=models.CharField(default=b'', max_length=1, blank=True, choices=[(b'C', b'Cadet'), (b'J', b'Junior'), (b'', b'Senior'), (b'M', b'Master')]),
        ),
    ]
