# Generated by Django 4.2.6 on 2023-10-25 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0038_last_login_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='scoring_system',
            field=models.CharField(choices=[('F', 'Full running slips'), ('D', 'Dozen running slips'), ('T', 'Totals only'), ('T', 'On archer mobile devices')], max_length=1),
        ),
    ]
