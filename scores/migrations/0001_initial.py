# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Arrow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('arrow_value', models.PositiveIntegerField()),
                ('arrow_of_round', models.PositiveIntegerField()),
                ('is_x', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Dozen',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('total', models.PositiveIntegerField()),
                ('dozen', models.PositiveIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.PositiveIntegerField(default=0, db_index=True)),
                ('hits', models.PositiveIntegerField(default=0)),
                ('golds', models.PositiveIntegerField(default=0)),
                ('xs', models.PositiveIntegerField(default=0)),
                ('alteration', models.IntegerField(default=0)),
                ('retired', models.BooleanField(default=False)),
                ('disqualified', models.BooleanField(default=False)),
                ('target', models.OneToOneField(to='entries.TargetAllocation')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='dozen',
            name='score',
            field=models.ForeignKey(to='scores.Score'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='arrow',
            name='score',
            field=models.ForeignKey(to='scores.Score'),
            preserve_default=True,
        ),
    ]
