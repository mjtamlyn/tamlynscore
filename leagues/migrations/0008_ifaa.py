# Generated by Django 4.1.2 on 2023-02-03 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0007_remove_wa_and_jm_age_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='leg',
            name='ifaa_rules',
            field=models.BooleanField(default=False),
        ),
    ]
