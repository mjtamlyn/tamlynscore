# -*- coding: utf-8 -*-

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0007_auto_20150621_0620'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competitionentry',
            name='wa_age',
            field=models.CharField(default='', max_length=1, blank=True, choices=[('C', 'Cadet'), ('J', 'Junior'), ('', 'Senior'), ('M', 'Master')]),
        ),
    ]
