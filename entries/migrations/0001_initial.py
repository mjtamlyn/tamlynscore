# -*- coding: utf-8 -*-

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
                ('exclude_later_shoots', models.BooleanField(default=False, help_text='Only the first session can count for results')),
                ('strict_b_teams', models.BooleanField(default=False, help_text='e.g. BUTC')),
                ('strict_c_teams', models.BooleanField(default=False, help_text='e.g. BUTC')),
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
                ('age', models.CharField(default='S', max_length=1, choices=[('J', 'Junior'), ('S', 'Senior')])),
                ('novice', models.CharField(default='E', max_length=1, choices=[('N', 'Novice'), ('E', 'Experienced')])),
                ('guest', models.BooleanField(default=False)),
                ('b_team', models.BooleanField(default=False)),
                ('c_team', models.BooleanField(default=False)),
                ('archer', models.ForeignKey(to='core.Archer', on_delete=models.CASCADE)),
                ('bowstyle', models.ForeignKey(to='core.Bowstyle', on_delete=models.CASCADE)),
                ('club', models.ForeignKey(to='core.Club', on_delete=models.CASCADE)),
                ('competition', models.ForeignKey(to='entries.Competition', on_delete=models.CASCADE)),
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
                ('mode', models.CharField(max_length=31, choices=[('by-session', 'By session'), ('by-round', 'By round'), ('by-round-progressional', 'By round (progressional)'), ('double-round', 'Double round'), ('seedings', 'Seedings'), ('team', 'Teams'), ('weekend', 'Weekend (Masters style)')])),
                ('leaderboard_only', models.BooleanField(default=False)),
                ('competition', models.ForeignKey(related_name='result_modes', to='entries.Competition', on_delete=models.CASCADE)),
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
                ('scoring_system', models.CharField(max_length=1, choices=[('F', 'Full running slips'), ('D', 'Dozen running slips'), ('T', 'Totals only')])),
                ('archers_per_target', models.IntegerField()),
                ('arrows_entered_per_end', models.IntegerField(default=12)),
                ('competition', models.ForeignKey(to='entries.Competition', on_delete=models.CASCADE)),
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
                ('competition_entry', models.ForeignKey(to='entries.CompetitionEntry', on_delete=models.CASCADE)),
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
                ('session', models.ForeignKey(to='entries.Session', on_delete=models.CASCADE)),
                ('shot_round', models.ForeignKey(to='core.Round', on_delete=models.CASCADE)),
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
                ('logo', models.ImageField(upload_to='sponsors')),
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
                ('session_entry', models.OneToOneField(to='entries.SessionEntry', on_delete=models.CASCADE)),
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
                ('host_club', models.ForeignKey(to='core.Club', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sessionentry',
            name='session_round',
            field=models.ForeignKey(to='entries.SessionRound', on_delete=models.CASCADE),
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
            field=models.ForeignKey(to='entries.Tournament', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='competition',
            unique_together=set([('date', 'tournament')]),
        ),
    ]
