# Generated by Django 4.1.2 on 2023-02-06 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_round_is_ifaa'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='flint_round',
            field=models.BooleanField(default=False),
        ),
    ]
