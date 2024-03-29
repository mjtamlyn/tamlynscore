# Generated by Django 4.1.2 on 2023-02-03 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0026_wa_age_group_changes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competitionentry',
            name='agb_age',
            field=models.CharField(blank=True, choices=[('65+', '65+'), ('50+', '50+'), ('', 'Senior'), ('U21', 'U21'), ('U18', 'U18'), ('U16', 'U16'), ('U15', 'U15'), ('U14', 'U14'), ('U12', 'U12'), ('U10', 'U10')], default='', max_length=3),
        ),
    ]
