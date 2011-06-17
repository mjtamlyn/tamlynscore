# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'BoundRound'
        db.create_table('records_boundround', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('round_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['records.Round'])),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['records.Competition'])),
        ))
        db.send_create_signal('records', ['BoundRound'])

        # Removing M2M table for field rounds on 'Competition'
        db.delete_table('records_competition_rounds')

        # Deleting field 'Entry.competition'
        db.delete_column('records_entry', 'competition_id')

        # Adding field 'Entry.shot_round'
        db.add_column('records_entry', 'shot_round', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['records.BoundRound']), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'BoundRound'
        db.delete_table('records_boundround')

        # Adding M2M table for field rounds on 'Competition'
        db.create_table('records_competition_rounds', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('competition', models.ForeignKey(orm['records.competition'], null=False)),
            ('round', models.ForeignKey(orm['records.round'], null=False))
        ))
        db.create_unique('records_competition_rounds', ['competition_id', 'round_id'])

        # User chose to not deal with backwards NULL issues for 'Entry.competition'
        raise RuntimeError("Cannot reverse this migration. 'Entry.competition' and its values cannot be restored.")

        # Deleting field 'Entry.shot_round'
        db.delete_column('records_entry', 'shot_round_id')


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
        'records.boundround': {
            'Meta': {'object_name': 'BoundRound'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Competition']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'round_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Round']"})
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
            'rounds': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['records.Round']", 'through': "orm['records.BoundRound']", 'symmetrical': 'False'}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Tournament']"})
        },
        'records.entry': {
            'Meta': {'object_name': 'Entry'},
            'archer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Archer']"}),
            'bowstyle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Bowstyle']"}),
            'club': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.Club']"}),
            'golds': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'hits': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'shot_round': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['records.BoundRound']"})
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
