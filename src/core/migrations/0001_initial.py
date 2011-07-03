# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Subround'
        db.create_table('core_subround', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('arrows', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('distance', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('unit', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('target_face', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('core', ['Subround'])

        # Adding model 'Round'
        db.create_table('core_round', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('scoring_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('core', ['Round'])

        # Adding M2M table for field subrounds on 'Round'
        db.create_table('core_round_subrounds', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('round', models.ForeignKey(orm['core.round'], null=False)),
            ('subround', models.ForeignKey(orm['core.subround'], null=False))
        ))
        db.create_unique('core_round_subrounds', ['round_id', 'subround_id'])

        # Adding model 'Bowstyle'
        db.create_table('core_bowstyle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal('core', ['Bowstyle'])

        # Adding model 'Club'
        db.create_table('core_club', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=500)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal('core', ['Club'])

        # Adding model 'Archer'
        db.create_table('core_archer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('club', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Club'])),
            ('bowstyle', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Bowstyle'])),
            ('age', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('novice', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('core', ['Archer'])


    def backwards(self, orm):
        
        # Deleting model 'Subround'
        db.delete_table('core_subround')

        # Deleting model 'Round'
        db.delete_table('core_round')

        # Removing M2M table for field subrounds on 'Round'
        db.delete_table('core_round_subrounds')

        # Deleting model 'Bowstyle'
        db.delete_table('core_bowstyle')

        # Deleting model 'Club'
        db.delete_table('core_club')

        # Deleting model 'Archer'
        db.delete_table('core_archer')


    models = {
        'core.archer': {
            'Meta': {'object_name': 'Archer'},
            'age': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'bowstyle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Bowstyle']"}),
            'club': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Club']"}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'novice': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
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
        }
    }

    complete_apps = ['core']
