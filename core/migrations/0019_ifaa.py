# Generated by Django 4.1.2 on 2023-02-03 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_remove_wa_and_jm_age_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='bowstyle',
            name='ifaa_only',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='archer',
            name='agb_age',
            field=models.CharField(blank=True, choices=[('', 'Senior'), ('50+', '50+'), ('65+', '65+'), ('U21', 'U21'), ('U18', 'U18'), ('U16', 'U16'), ('U15', 'U15'), ('U14', 'U14'), ('U12', 'U12'), ('U10', 'U10')], default='', max_length=3),
        ),
    ]
