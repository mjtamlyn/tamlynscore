# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('end_date', models.DateField(null=True, blank=True)),
                ('slug', models.SlugField(unique=True, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('has_novices', models.BooleanField(default=False)),
                ('has_juniors', models.BooleanField(default=False)),
                ('has_teams', models.BooleanField(default=False)),
                ('novices_in_experienced_teams', models.BooleanField(default=False)),
                ('exclude_later_shoots', models.BooleanField(default=False, help_text=b'Only the first session can count for results')),
                ('strict_b_teams', models.BooleanField(default=False, help_text=b'e.g. BUTC')),
                ('strict_c_teams', models.BooleanField(default=False, help_text=b'e.g. BUTC')),
                ('allow_incomplete_teams', models.BooleanField(default=True)),
                ('team_size', models.PositiveIntegerField(default=4)),
                ('novice_team_size', models.PositiveIntegerField(default=3)),
                ('compound_team_size', models.PositiveIntegerField(default=None, null=True, blank=True)),
                ('junior_team_size', models.PositiveIntegerField(default=None, null=True, blank=True)),
                ('force_mixed_teams', models.BooleanField(default=False)),
                ('combine_rounds_for_team_scores', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CompetitionEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('age', models.CharField(default=b'S', max_length=1, choices=[(b'J', b'Junior'), (b'S', b'Senior')])),
                ('novice', models.CharField(default=b'E', max_length=1, choices=[(b'N', b'Novice'), (b'E', b'Experienced')])),
                ('guest', models.BooleanField(default=False)),
                ('b_team', models.BooleanField(default=False)),
                ('c_team', models.BooleanField(default=False)),
                ('archer', models.ForeignKey(to='core.Archer')),
                ('bowstyle', models.ForeignKey(to='core.Bowstyle')),
                ('club', models.ForeignKey(to='core.Club')),
                ('competition', models.ForeignKey(to='entries.Competition')),
            ],
            options={
                'verbose_name_plural': 'competition entries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResultsMode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mode', models.CharField(max_length=31, choices=[(b'by-session', b'By session'), (b'by-round', b'By round'), (b'by-round-progressional', b'By round (progressional)'), (b'double-round', b'Double round'), (b'seedings', b'Seedings'), (b'team', b'Teams'), (b'weekend', b'Weekend (Masters style)')])),
                ('leaderboard_only', models.BooleanField(default=False)),
                ('competition', models.ForeignKey(related_name='result_modes', to='entries.Competition')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateTimeField()),
                ('scoring_system', models.CharField(max_length=1, choices=[(b'F', b'Full running slips'), (b'D', b'Dozen running slips'), (b'T', b'Totals only')])),
                ('archers_per_target', models.IntegerField()),
                ('arrows_entered_per_end', models.IntegerField(default=12)),
                ('competition', models.ForeignKey(to='entries.Competition')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SessionEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('present', models.BooleanField(default=False)),
                ('index', models.PositiveIntegerField(default=1)),
                ('competition_entry', models.ForeignKey(to='entries.CompetitionEntry')),
            ],
            options={
                'verbose_name_plural': 'session entries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SessionRound',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('session', models.ForeignKey(to='entries.Session')),
                ('shot_round', models.ForeignKey(to='core.Round')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('logo', models.ImageField(upload_to=b'sponsors')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TargetAllocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('boss', models.PositiveIntegerField()),
                ('target', models.CharField(max_length=1)),
                ('session_entry', models.OneToOneField(to='entries.SessionEntry')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('full_name', models.CharField(unique=True, max_length=300)),
                ('short_name', models.CharField(max_length=20)),
                ('host_club', models.ForeignKey(to='core.Club')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sessionentry',
            name='session_round',
            field=models.ForeignKey(to='entries.SessionRound'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='resultsmode',
            unique_together=set([('competition', 'mode')]),
        ),
        migrations.AddField(
            model_name='competition',
            name='sponsors',
            field=models.ManyToManyField(to='entries.Sponsor', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='competition',
            name='tournament',
            field=models.ForeignKey(to='entries.Tournament'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='competition',
            unique_together=set([('date', 'tournament')]),
        ),
    ]
