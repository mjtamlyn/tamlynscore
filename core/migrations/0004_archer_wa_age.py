# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_club_abbreviation'),
    ]

    operations = [
        migrations.AddField(
            model_name='archer',
            name='wa_age',
            field=models.CharField(default='', max_length=1, choices=[('C', 'Cadet'), ('J', 'Junior'), ('', 'Senior'), ('M', 'Master')]),
        ),
    ]
