# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Arrow.is_x'
        db.add_column('records_arrow', 'is_x', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Arrow.is_x'
        db.delete_column('records_arrow', 'is_x')


    models = {
        'records.archer': {
            'Meta': {'unique_together': "(('name', 'club'),)", 'object_name': 'Archer'},
            'bowstyle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Bowstyle']"}),
            'club': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Club']"}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'records.arrow': {
            'Meta': {'unique_together': "(('subround', 'arrow_of_round', 'entry'),)", 'object_name': 'Arrow'},
            'arrow_of_round': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_x': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'score': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'subround': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Subround']"})
        },
        'records.boundround': {
            'Meta': {'object_name': 'BoundRound'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Competition']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'round_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Round']"}),
            'use_individual_arrows': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'records.bowstyle': {
            'Meta': {'object_name': 'Bowstyle'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'records.club': {
            'Meta': {'object_name': 'Club'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '500'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'records.competition': {
            'Meta': {'unique_together': "(('date', 'tournament'),)", 'object_name': 'Competition'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'rounds': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['records.Round']", 'through': "orm['records.BoundRound']", 'symmetrical': 'False'}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Tournament']"})
        },
        'records.entry': {
            'Meta': {'unique_together': "(('archer', 'shot_round'),)", 'object_name': 'Entry'},
            'archer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Archer']"}),
            'bowstyle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Bowstyle']"}),
            'club': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Club']"}),
            'golds': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'hits': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'shot_round': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.BoundRound']"}),
            'target': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'records.round': {
            'Meta': {'object_name': 'Round'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'subrounds': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['records.Subround']", 'symmetrical': 'False'})
        },
        'records.subround': {
            'Meta': {'object_name': 'Subround'},
            'arrows': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'distance': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'records.tournament': {
            'Meta': {'object_name': 'Tournament'},
            'full_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '300'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['records']
