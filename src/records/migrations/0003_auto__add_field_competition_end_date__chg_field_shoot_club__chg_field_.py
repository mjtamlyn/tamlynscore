# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Competition.end_date'
        db.add_column('records_competition', 'end_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True), keep_default=False)

        # Changing field 'Shoot.club'
        db.alter_column('records_shoot', 'club_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['records.Club'], null=True))

        # Changing field 'Shoot.bowstyle'
        db.alter_column('records_shoot', 'bowstyle_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['records.Bowstyle'], null=True))


    def backwards(self, orm):
        
        # Deleting field 'Competition.end_date'
        db.delete_column('records_competition', 'end_date')

        # Changing field 'Shoot.club'
        db.alter_column('records_shoot', 'club_id', self.gf('django.db.models.fields.related.ForeignKey')(default=datetime.datetime(2011, 6, 10, 21, 55, 12, 450327), to=orm['records.Club']))

        # Changing field 'Shoot.bowstyle'
        db.alter_column('records_shoot', 'bowstyle_id', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['records.Bowstyle']))


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
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'records.shoot': {
            'Meta': {'object_name': 'Shoot'},
            'archer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Archer']"}),
            'bowstyle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Bowstyle']", 'null': 'True', 'blank': 'True'}),
            'club': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Club']", 'null': 'True', 'blank': 'True'}),
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Competition']"}),
            'golds': ('django.db.models.fields.IntegerField', [], {}),
            'hits': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['records']
