# -*- coding: utf-8 -*-

from django.db import migrations, models


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
