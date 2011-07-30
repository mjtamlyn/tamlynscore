# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'OlympicRound'
        db.create_table('olympic_olympicround', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('distance', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('match_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('olympic', ['OlympicRound'])

        # Adding model 'Category'
        db.create_table('olympic_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('olympic', ['Category'])

        # Adding M2M table for field bowstyles on 'Category'
        db.create_table('olympic_category_bowstyles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('category', models.ForeignKey(orm['olympic.category'], null=False)),
            ('bowstyle', models.ForeignKey(orm['core.bowstyle'], null=False))
        ))
        db.create_unique('olympic_category_bowstyles', ['category_id', 'bowstyle_id'])

        # Adding model 'OlympicSessionRound'
        db.create_table('olympic_olympicsessionround', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entries.Session'])),
            ('shot_round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['olympic.OlympicRound'])),
            ('ranking_round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entries.SessionRound'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['olympic.Category'])),
        ))
        db.send_create_signal('olympic', ['OlympicSessionRound'])

        # Adding model 'Seeding'
        db.create_table('olympic_seeding', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entries.CompetitionEntry'])),
            ('session_round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['olympic.OlympicSessionRound'])),
            ('seed', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('olympic', ['Seeding'])

        # Adding model 'Match'
        db.create_table('olympic_match', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('session_round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['olympic.OlympicSessionRound'])),
            ('target', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('match', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('olympic', ['Match'])

        # Adding model 'Result'
        db.create_table('olympic_result', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('match', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['olympic.Match'])),
            ('winner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='result_winner_set', to=orm['olympic.Seeding'])),
            ('loser', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='result_loser_set', null=True, to=orm['olympic.Seeding'])),
        ))
        db.send_create_signal('olympic', ['Result'])


    def backwards(self, orm):
        
        # Deleting model 'OlympicRound'
        db.delete_table('olympic_olympicround')

        # Deleting model 'Category'
        db.delete_table('olympic_category')

        # Removing M2M table for field bowstyles on 'Category'
        db.delete_table('olympic_category_bowstyles')

        # Deleting model 'OlympicSessionRound'
        db.delete_table('olympic_olympicsessionround')

        # Deleting model 'Seeding'
        db.delete_table('olympic_seeding')

        # Deleting model 'Match'
        db.delete_table('olympic_match')

        # Deleting model 'Result'
        db.delete_table('olympic_result')


    models = {
        'core.archer': {
            'Meta': {'object_name': 'Archer'},
            'age': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'bowstyle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Bowstyle']"}),
            'club': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Club']"}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'gnas_no': ('django.db.models.fields.BigIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'novice': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'core.bowstyle': {
            'Meta': {'object_name': 'Bowstyle'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'core.club': {
            'Meta': {'object_name': 'Club'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '500'}),
            'short_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        },
        'core.round': {
            'Meta': {'object_name': 'Round'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'scoring_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'subrounds': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Subround']", 'symmetrical': 'False'})
        },
        'core.subround': {
            'Meta': {'object_name': 'Subround'},
            'arrows': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'distance': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'target_face': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'entries.competition': {
            'Meta': {'unique_together': "(('date', 'tournament'),)", 'object_name': 'Competition'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entries.Tournament']"})
        },
        'entries.competitionentry': {
            'Meta': {'object_name': 'CompetitionEntry'},
            'age': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'archer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Archer']"}),
            'bowstyle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Bowstyle']"}),
            'club': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Club']"}),
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entries.Competition']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'novice': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'entries.session': {
            'Meta': {'object_name': 'Session'},
            'archers_per_target': ('django.db.models.fields.IntegerField', [], {}),
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entries.Competition']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scoring_system': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'start': ('django.db.models.fields.DateTimeField', [], {})
        },
        'entries.sessionround': {
            'Meta': {'object_name': 'SessionRound'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entries.Session']"}),
            'shot_round': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Round']"})
        },
        'entries.tournament': {
            'Meta': {'object_name': 'Tournament'},
            'full_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '300'}),
            'host_club': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Club']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'olympic.category': {
            'Meta': {'object_name': 'Category'},
            'bowstyles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Bowstyle']", 'symmetrical': 'False'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'olympic.match': {
            'Meta': {'object_name': 'Match'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'match': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'session_round': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['olympic.OlympicSessionRound']"}),
            'target': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'olympic.olympicround': {
            'Meta': {'object_name': 'OlympicRound'},
            'distance': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'olympic.olympicsessionround': {
            'Meta': {'object_name': 'OlympicSessionRound'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['olympic.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ranking_round': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entries.SessionRound']"}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entries.Session']"}),
            'shot_round': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['olympic.OlympicRound']"})
        },
        'olympic.result': {
            'Meta': {'object_name': 'Result'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'loser': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'result_loser_set'", 'null': 'True', 'to': "orm['olympic.Seeding']"}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['olympic.Match']"}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'result_winner_set'", 'to': "orm['olympic.Seeding']"})
        },
        'olympic.seeding': {
            'Meta': {'object_name': 'Seeding'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entries.CompetitionEntry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'seed': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'session_round': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['olympic.OlympicSessionRound']"})
        }
    }

    complete_apps = ['olympic']
