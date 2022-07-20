# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_archer_wa_age'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archer',
            name='wa_age',
            field=models.CharField(default='', max_length=1, blank=True, choices=[('C', 'Cadet'), ('J', 'Junior'), ('', 'Senior'), ('M', 'Master')]),
        ),
    ]
