# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0018_add_novices_exp_individual'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='has_guests',
            field=models.BooleanField(default=False),
        ),
    ]
