# Generated by Django 4.2.6 on 2023-12-02 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0040_fix_archer_scoring'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='any_bow_team_size',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]