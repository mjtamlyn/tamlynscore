# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Archer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('gender', models.CharField(max_length=1, choices=[(b'G', b'Gent'), (b'L', b'Lady')])),
                ('age', models.CharField(default=b'S', max_length=1, choices=[(b'J', b'Junior'), (b'S', b'Senior')])),
                ('novice', models.CharField(default=b'E', max_length=1, choices=[(b'N', b'Novice'), (b'E', b'Experienced')])),
                ('gnas_no', models.BigIntegerField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Bowstyle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=500)),
                ('short_name', models.CharField(unique=True, max_length=50)),
                ('abbreviation', models.CharField(default=b'', max_length=10, blank=True)),
                ('slug', models.SlugField(unique=True, editable=False)),
            ],
            options={
                'ordering': ('short_name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
            ],
            options={
                'verbose_name_plural': 'countries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='County',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
            ],
            options={
                'verbose_name_plural': 'counties',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('country', models.ForeignKey(to='core.Country')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Round',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('scoring_type', models.CharField(max_length=1, choices=[(b'F', b'Five Zone Imperial'), (b'T', b'AGB Indoor - Ten Zone, no Xs, with hits'), (b'X', b'WA Outdoor - Ten Zone, with Xs, no hits'), (b'I', b'WA Indoor - Ten Zone, no Xs, no hits'), (b'W', b'Worcester')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subround',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('arrows', models.PositiveIntegerField()),
                ('distance', models.PositiveIntegerField()),
                ('unit', models.CharField(max_length=1, choices=[(b'm', b'metres'), (b'y', b'yards')])),
                ('target_face', models.PositiveIntegerField()),
            ],
            options={
                'ordering': ('unit', '-distance', '-arrows', '-target_face'),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='round',
            name='subrounds',
            field=models.ManyToManyField(to='core.Subround'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='county',
            name='region',
            field=models.ForeignKey(to='core.Region'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='club',
            name='county',
            field=models.ForeignKey(blank=True, to='core.County', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='archer',
            name='bowstyle',
            field=models.ForeignKey(to='core.Bowstyle'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='archer',
            name='club',
            field=models.ForeignKey(to='core.Club'),
            preserve_default=True,
        ),
    ]
