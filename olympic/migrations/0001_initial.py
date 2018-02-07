# -*- coding: utf-8 -*-

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gender', models.CharField(blank=True, max_length=1, null=True, choices=[('G', 'Gent'), ('L', 'Lady')])),
                ('bowstyles', models.ManyToManyField(to='core.Bowstyle')),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('target', models.PositiveIntegerField()),
                ('target_2', models.PositiveIntegerField(null=True, blank=True)),
                ('level', models.PositiveIntegerField()),
                ('match', models.PositiveIntegerField()),
                ('timing', models.PositiveIntegerField(null=True)),
            ],
            options={
                'verbose_name_plural': 'matches',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OlympicRound',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('distance', models.PositiveIntegerField()),
                ('match_type', models.CharField(max_length=1, choices=[('T', 'Sets'), ('C', 'Score')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OlympicSessionRound',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.ForeignKey(to='olympic.Category', on_delete=models.CASCADE)),
                ('ranking_round', models.ForeignKey(to='entries.SessionRound', on_delete=models.CASCADE)),
                ('session', models.ForeignKey(to='entries.Session', on_delete=models.CASCADE)),
                ('shot_round', models.ForeignKey(to='olympic.OlympicRound', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('total', models.PositiveIntegerField()),
                ('arrow_total', models.PositiveIntegerField(default=0)),
                ('win', models.BooleanField(default=False)),
                ('dns', models.BooleanField(default=False)),
                ('win_by_forfeit', models.BooleanField(default=False)),
                ('match', models.ForeignKey(to='olympic.Match', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Seeding',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('seed', models.PositiveIntegerField()),
                ('entry', models.ForeignKey(to='entries.CompetitionEntry', on_delete=models.CASCADE)),
                ('session_round', models.ForeignKey(to='olympic.OlympicSessionRound', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='result',
            name='seed',
            field=models.ForeignKey(to='olympic.Seeding', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='match',
            name='session_round',
            field=models.ForeignKey(to='olympic.OlympicSessionRound', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
