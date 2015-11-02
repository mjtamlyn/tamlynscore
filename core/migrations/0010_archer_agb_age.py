# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='archer',
            name='agb_age',
            field=models.CharField(blank=True, max_length=3, choices=[('', 'Senior'), ('U18', 'U18'), ('U16', 'U16'), ('U14', 'U14'), ('U12', 'U12')], default=''),
        ),
    ]
