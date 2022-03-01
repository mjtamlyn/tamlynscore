# Generated by Django 3.2.9 on 2022-03-01 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_add_extra_age_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='can_split',
            field=models.BooleanField(default=False, help_text='If the round does not have multiple subrounds, but it makes sense to talk about two halves of the round (e.g. a WA18m or WA70m), then tick this box and the split can be used in exports.'),
        ),
    ]