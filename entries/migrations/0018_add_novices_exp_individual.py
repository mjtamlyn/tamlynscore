# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0017_agb_age'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='novices_in_experienced_individual',
            field=models.BooleanField(help_text='Puts the novices in experienced results and their own category', default=False),
        ),
    ]
