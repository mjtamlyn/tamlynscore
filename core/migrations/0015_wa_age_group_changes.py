# Generated by Django 4.0.6 on 2022-08-11 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_split_rounds'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archer',
            name='wa_age',
            field=models.CharField(blank=True, choices=[('C', 'U18'), ('J', 'U21'), ('', 'Adult'), ('M', '50+'), ('N', '65+')], default='', max_length=1),
        ),
    ]
