# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Result.winner'
        db.delete_column('olympic_result', 'winner_id')

        # Deleting field 'Result.loser'
        db.delete_column('olympic_result', 'loser_id')

        # Adding field 'Result.seed'
        db.add_column('olympic_result', 'seed', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['olympic.Seeding']), keep_default=False)

        # Adding field 'Result.total'
        db.add_column('olympic_result', 'total', self.gf('django.db.models.fields.PositiveIntegerField')(default=0), keep_default=False)

        # Adding field 'Result.win'
        db.add_column('olympic_result', 'win', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'Result.winner'
        raise RuntimeError("Cannot reverse this migration. 'Result.winner' and its values cannot be restored.")

        # Adding field 'Result.loser'
        db.add_column('olympic_result', 'loser', self.gf('django.db.models.fields.related.ForeignKey')(related_name='result_loser_set', null=True, to=orm['olympic.Seeding'], blank=True), keep_default=False)

        # Deleting field 'Result.seed'
        db.delete_column('olympic_result', 'seed_id')

        # Deleting field 'Result.total'
        db.delete_column('olympic_result', 'total')

        # Deleting field 'Result.win'
        db.delete_column('olympic_result', 'win')


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
            'Meta': {'ordering': "('short_name',)", 'object_name': 'Club'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'county': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.County']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '500'}),
            'short_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        },
        'core.country': {
            'Meta': {'object_name': 'Country'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'core.county': {
            'Meta': {'object_name': 'County'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Region']"})
        },
        'core.region': {
            'Meta': {'object_name': 'Region'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
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
            'target': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'target_2': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
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
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['olympic.Match']"}),
            'seed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['olympic.Seeding']"}),
            'total': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'win': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
