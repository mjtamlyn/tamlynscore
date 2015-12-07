# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_archer_agb_age'),
        ('entries', '0019_competition_has_guests'),
    ]

    operations = [
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Leg',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('index', models.PositiveIntegerField()),
                ('clubs', models.ManyToManyField(to='core.Club')),
                ('competitions', models.ManyToManyField(to='entries.Competition')),
            ],
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('clubs', models.ManyToManyField(to='core.Club')),
                ('league', models.ForeignKey(to='leagues.League')),
            ],
        ),
        migrations.AddField(
            model_name='leg',
            name='season',
            field=models.ForeignKey(to='leagues.Season'),
        ),
    ]
