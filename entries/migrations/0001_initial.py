# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Tournament'
        db.create_table('entries_tournament', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('full_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=300)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('host_club', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Club'])),
        ))
        db.send_create_signal('entries', ['Tournament'])

        # Adding model 'Competition'
        db.create_table('entries_competition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tournament', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entries.Tournament'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('entries', ['Competition'])

        # Adding unique constraint on 'Competition', fields ['date', 'tournament']
        db.create_unique('entries_competition', ['date', 'tournament_id'])

        # Adding model 'Session'
        db.create_table('entries_session', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entries.Competition'])),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('scoring_system', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('entries', ['Session'])

        # Adding model 'SessionRound'
        db.create_table('entries_sessionround', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entries.Session'])),
            ('shot_round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Round'])),
        ))
        db.send_create_signal('entries', ['SessionRound'])

        # Adding model 'CompetitionEntry'
        db.create_table('entries_competitionentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entries.Competition'])),
            ('archer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Archer'])),
            ('club', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Club'])),
            ('bowstyle', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Bowstyle'])),
            ('age', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('novice', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('entries', ['CompetitionEntry'])

        # Adding model 'SessionEntry'
        db.create_table('entries_sessionentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition_entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entries.CompetitionEntry'])),
            ('session_round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entries.SessionRound'])),
        ))
        db.send_create_signal('entries', ['SessionEntry'])

        # Adding model 'TargetAllocation'
        db.create_table('entries_targetallocation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('session_entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['entries.SessionEntry'])),
            ('boss', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('target', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('entries', ['TargetAllocation'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Competition', fields ['date', 'tournament']
        db.delete_unique('entries_competition', ['date', 'tournament_id'])

        # Deleting model 'Tournament'
        db.delete_table('entries_tournament')

        # Deleting model 'Competition'
        db.delete_table('entries_competition')

        # Deleting model 'Session'
        db.delete_table('entries_session')

        # Deleting model 'SessionRound'
        db.delete_table('entries_sessionround')

        # Deleting model 'CompetitionEntry'
        db.delete_table('entries_competitionentry')

        # Deleting model 'SessionEntry'
        db.delete_table('entries_sessionentry')

        # Deleting model 'TargetAllocation'
        db.delete_table('entries_targetallocation')


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
            'novice': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'entries.session': {
            'Meta': {'object_name': 'Session'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entries.Competition']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scoring_system': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'start': ('django.db.models.fields.DateTimeField', [], {})
        },
        'entries.sessionentry': {
            'Meta': {'object_name': 'SessionEntry'},
            'competition_entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entries.CompetitionEntry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session_round': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entries.SessionRound']"})
        },
        'entries.sessionround': {
            'Meta': {'object_name': 'SessionRound'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entries.Session']"}),
            'shot_round': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Round']"})
        },
        'entries.targetallocation': {
            'Meta': {'object_name': 'TargetAllocation'},
            'boss': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session_entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entries.SessionEntry']"}),
            'target': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'entries.tournament': {
            'Meta': {'object_name': 'Tournament'},
            'full_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '300'}),
            'host_club': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Club']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['entries']
