# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Competition'
        db.create_table('records_competition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('records', ['Competition'])

        # Adding model 'Bowstyle'
        db.create_table('records_bowstyle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('records', ['Bowstyle'])

        # Adding model 'Club'
        db.create_table('records_club', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('records', ['Club'])

        # Adding model 'Archer'
        db.create_table('records_archer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('club', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['records.Club'])),
            ('bowstyle', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['records.Bowstyle'])),
        ))
        db.send_create_signal('records', ['Archer'])

        # Adding model 'Shoot'
        db.create_table('records_shoot', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('score', self.gf('django.db.models.fields.IntegerField')()),
            ('hits', self.gf('django.db.models.fields.IntegerField')()),
            ('golds', self.gf('django.db.models.fields.IntegerField')()),
            ('archer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['records.Archer'])),
            ('club', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['records.Club'], blank=True)),
            ('bowstyle', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['records.Bowstyle'], blank=True)),
        ))
        db.send_create_signal('records', ['Shoot'])


    def backwards(self, orm):
        
        # Deleting model 'Competition'
        db.delete_table('records_competition')

        # Deleting model 'Bowstyle'
        db.delete_table('records_bowstyle')

        # Deleting model 'Club'
        db.delete_table('records_club')

        # Deleting model 'Archer'
        db.delete_table('records_archer')

        # Deleting model 'Shoot'
        db.delete_table('records_shoot')


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'records.shoot': {
            'Meta': {'object_name': 'Shoot'},
            'archer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Archer']"}),
            'bowstyle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Bowstyle']", 'blank': 'True'}),
            'club': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Club']", 'blank': 'True'}),
            'golds': ('django.db.models.fields.IntegerField', [], {}),
            'hits': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['records']
