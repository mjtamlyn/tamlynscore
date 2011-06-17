# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Round'
        db.create_table('records_round', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('records', ['Round'])

        # Adding M2M table for field subrounds on 'Round'
        db.create_table('records_round_subrounds', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('round', models.ForeignKey(orm['records.round'], null=False)),
            ('subround', models.ForeignKey(orm['records.subround'], null=False))
        ))
        db.create_unique('records_round_subrounds', ['round_id', 'subround_id'])

        # Adding model 'Arrow'
        db.create_table('records_arrow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subround', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['records.Subround'])),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['records.Entry'])),
            ('score', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('arrow_of_round', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('records', ['Arrow'])

        # Adding model 'Subround'
        db.create_table('records_subround', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('arrows', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('distance', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('unit', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('records', ['Subround'])

        # Adding model 'Tournament'
        db.create_table('records_tournament', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('records', ['Tournament'])

        # Adding M2M table for field rounds on 'Competition'
        db.create_table('records_competition_rounds', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('competition', models.ForeignKey(orm['records.competition'], null=False)),
            ('round', models.ForeignKey(orm['records.round'], null=False))
        ))
        db.create_unique('records_competition_rounds', ['competition_id', 'round_id'])


    def backwards(self, orm):
        
        # Deleting model 'Round'
        db.delete_table('records_round')

        # Removing M2M table for field subrounds on 'Round'
        db.delete_table('records_round_subrounds')

        # Deleting model 'Arrow'
        db.delete_table('records_arrow')

        # Deleting model 'Subround'
        db.delete_table('records_subround')

        # Deleting model 'Tournament'
        db.delete_table('records_tournament')

        # Removing M2M table for field rounds on 'Competition'
        db.delete_table('records_competition_rounds')


    models = {
        'records.archer': {
            'Meta': {'object_name': 'Archer'},
            'bowstyle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Bowstyle']"}),
            'club': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Club']"}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'records.arrow': {
            'Meta': {'object_name': 'Arrow'},
            'arrow_of_round': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'subround': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Subround']"})
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
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'rounds': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['records.Round']", 'symmetrical': 'False'})
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
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['records']
