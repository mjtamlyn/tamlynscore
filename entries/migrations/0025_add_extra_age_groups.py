# Generated by Django 3.2.9 on 2022-02-22 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0024_recurve_barebow_teams'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competitionentry',
            name='agb_age',
            field=models.CharField(blank=True, choices=[('50+', '50+'), ('', 'Senior'), ('U18', 'U18'), ('U16', 'U16'), ('U14', 'U14'), ('U12', 'U12'), ('U10', 'U10')], default='', max_length=3),
        ),
    ]
