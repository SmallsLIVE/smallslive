# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Event.endday'
        db.delete_column(u'events_event', 'endday')

        # Deleting field 'Event.datefreeform'
        db.delete_column(u'events_event', 'datefreeform')

        # Deleting field 'Event.startday'
        db.delete_column(u'events_event', 'startday')

        # Adding field 'Event.start_day'
        db.add_column(u'events_event', 'start_day',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Event.end_day'
        db.add_column(u'events_event', 'end_day',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Event.date_freeform'
        db.add_column(u'events_event', 'date_freeform',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Event.endday'
        db.add_column(u'events_event', 'endday',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Event.datefreeform'
        db.add_column(u'events_event', 'datefreeform',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Event.startday'
        db.add_column(u'events_event', 'startday',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Event.start_day'
        db.delete_column(u'events_event', 'start_day')

        # Deleting field 'Event.end_day'
        db.delete_column(u'events_event', 'end_day')

        # Deleting field 'Event.date_freeform'
        db.delete_column(u'events_event', 'date_freeform')


    models = {
        u'artists.artist': {
            'Meta': {'ordering': "['lastname']", 'object_name': 'Artist'},
            'artist_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['artists.ArtistType']", 'null': 'True', 'blank': 'True'}),
            'biography': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'salutation': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'templateid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'artists.artisttype': {
            'Meta': {'object_name': 'ArtistType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'events.event': {
            'Meta': {'ordering': "['-start_day']", 'object_name': 'Event'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date_freeform': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end_day': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'event_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.EventType']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'performers': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['artists.Artist']", 'through': u"orm['events.GigPlayed']", 'symmetrical': 'False'}),
            'start_day': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'subtitle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'events.eventtype': {
            'Meta': {'object_name': 'EventType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'parent': ('django.db.models.fields.IntegerField', [], {})
        },
        u'events.gigplayed': {
            'Meta': {'object_name': 'GigPlayed'},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'gigs_played'", 'to': u"orm['artists.Artist']"}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'artists_gig_info'", 'to': u"orm['events.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['artists.ArtistType']"}),
            'sort_order': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        }
    }

    complete_apps = ['events']