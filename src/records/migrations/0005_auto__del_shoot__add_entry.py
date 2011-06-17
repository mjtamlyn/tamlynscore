# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'Shoot'
        db.delete_table('records_shoot')

        # Adding model 'Entry'
        db.create_table('records_entry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['records.Competition'])),
            ('archer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['records.Archer'])),
            ('club', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['records.Club'])),
            ('bowstyle', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['records.Bowstyle'])),
            ('score', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('hits', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('golds', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('records', ['Entry'])


    def backwards(self, orm):
        
        # Adding model 'Shoot'
        db.create_table('records_shoot', (
            ('golds', self.gf('django.db.models.fields.IntegerField')()),
            ('hits', self.gf('django.db.models.fields.IntegerField')()),
            ('bowstyle', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['records.Bowstyle'], null=True, blank=True)),
            ('club', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['records.Club'], null=True, blank=True)),
            ('score', self.gf('django.db.models.fields.IntegerField')()),
            ('archer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['records.Archer'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['records.Competition'])),
        ))
        db.send_create_signal('records', ['Shoot'])

        # Deleting model 'Entry'
        db.delete_table('records_entry')


    models = {
        'records.archer': {
            'Meta': {'object_name': 'Archer'},
            'bowstyle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Bowstyle']"}),
            'club': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Club']"}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'records.bowstyle': {
            'Meta': {'object_name': 'Bowstyle'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'records.club': {
            'Meta': {'object_name': 'Club'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'records.competition': {
            'Meta': {'object_name': 'Competition'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'records.entry': {
            'Meta': {'object_name': 'Entry'},
            'archer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Archer']"}),
            'bowstyle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Bowstyle']"}),
            'club': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Club']"}),
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Competition']"}),
            'golds': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'hits': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['records']
