# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0012_make_novice_team_size_nullable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='host_club',
            field=models.ForeignKey(null=True, to='core.Club', blank=True, on_delete=models.CASCADE),
        ),
    ]
