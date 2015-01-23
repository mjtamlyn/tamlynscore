# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Result.dns'
        db.add_column(u'olympic_result', 'dns',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Result.win_by_forfeit'
        db.add_column(u'olympic_result', 'win_by_forfeit',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Result.dns'
        db.delete_column(u'olympic_result', 'dns')

        # Deleting field 'Result.win_by_forfeit'
        db.delete_column(u'olympic_result', 'win_by_forfeit')


    models = {
        u'core.archer': {
            'Meta': {'object_name': 'Archer'},
            'age': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'bowstyle': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Bowstyle']"}),
            'club': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Club']"}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'gnas_no': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'novice': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'core.bowstyle': {
            'Meta': {'object_name': 'Bowstyle'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'core.club': {
            'Meta': {'ordering': "('short_name',)", 'object_name': 'Club'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'blank': 'True'}),
            'county': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.County']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '500'}),
            'short_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'core.country': {
            'Meta': {'object_name': 'Country'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'core.county': {
            'Meta': {'object_name': 'County'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Region']"})
        },
        u'core.region': {
            'Meta': {'object_name': 'Region'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Country']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'core.round': {
            'Meta': {'object_name': 'Round'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'scoring_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'subrounds': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['core.Subround']", 'symmetrical': 'False'})
        },
        u'core.subround': {
            'Meta': {'ordering': "('unit', '-distance', '-arrows', '-target_face')", 'object_name': 'Subround'},
            'arrows': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'distance': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'target_face': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'entries.competition': {
            'Meta': {'unique_together': "(('date', 'tournament'),)", 'object_name': 'Competition'},
            'allow_incomplete_teams': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'combine_rounds_for_team_scores': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'compound_team_size': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'exclude_later_shoots': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'force_mixed_teams': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_juniors': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_novices': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_teams': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'novice_team_size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '3'}),
            'novices_in_experienced_teams': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'sponsors': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['entries.Sponsor']", 'symmetrical': 'False', 'blank': 'True'}),
            'strict_b_teams': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'strict_c_teams': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'team_size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '4'}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entries.Tournament']"})
        },
        u'entries.competitionentry': {
            'Meta': {'object_name': 'CompetitionEntry'},
            'age': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'archer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Archer']"}),
            'b_team': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bowstyle': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Bowstyle']"}),
            'c_team': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'club': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Club']"}),
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entries.Competition']"}),
            'guest': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'novice': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'entries.session': {
            'Meta': {'object_name': 'Session'},
            'archers_per_target': ('django.db.models.fields.IntegerField', [], {}),
            'arrows_entered_per_end': ('django.db.models.fields.IntegerField', [], {'default': '12'}),
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entries.Competition']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scoring_system': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'start': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'entries.sessionround': {
            'Meta': {'object_name': 'SessionRound'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entries.Session']"}),
            'shot_round': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Round']"})
        },
        u'entries.sponsor': {
            'Meta': {'object_name': 'Sponsor'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'entries.tournament': {
            'Meta': {'object_name': 'Tournament'},
            'full_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '300'}),
            'host_club': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Club']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'olympic.category': {
            'Meta': {'object_name': 'Category'},
            'bowstyles': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['core.Bowstyle']", 'symmetrical': 'False'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'olympic.match': {
            'Meta': {'object_name': 'Match'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'match': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'session_round': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['olympic.OlympicSessionRound']"}),
            'target': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'target_2': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'timing': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'})
        },
        u'olympic.olympicround': {
            'Meta': {'object_name': 'OlympicRound'},
            'distance': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'olympic.olympicsessionround': {
            'Meta': {'object_name': 'OlympicSessionRound'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['olympic.Category']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ranking_round': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entries.SessionRound']"}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entries.Session']"}),
            'shot_round': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['olympic.OlympicRound']"})
        },
        u'olympic.result': {
            'Meta': {'object_name': 'Result'},
            'arrow_total': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'dns': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['olympic.Match']"}),
            'seed': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['olympic.Seeding']"}),
            'total': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'win': ('django.db.models.fields.BooleanField', [], {}),
            'win_by_forfeit': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'olympic.seeding': {
            'Meta': {'object_name': 'Seeding'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entries.CompetitionEntry']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'seed': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'session_round': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['olympic.OlympicSessionRound']"})
        }
    }

    complete_apps = ['olympic']