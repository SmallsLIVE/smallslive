# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Event.presenterfreeform'
        db.delete_column(u'events_event', 'presenterfreeform')

        # Deleting field 'Event.city'
        db.delete_column(u'events_event', 'city')

        # Deleting field 'Event.zip'
        db.delete_column(u'events_event', 'zip')

        # Deleting field 'Event.state'
        db.delete_column(u'events_event', 'state')

        # Deleting field 'Event.location'
        db.delete_column(u'events_event', 'location')

        # Deleting field 'Event.extrainformation'
        db.delete_column(u'events_event', 'extrainformation')

        # Deleting field 'Event.email'
        db.delete_column(u'events_event', 'email')

        # Deleting field 'Event.tickets'
        db.delete_column(u'events_event', 'tickets')

        # Deleting field 'Event.displaydescription'
        db.delete_column(u'events_event', 'displaydescription')

        # Deleting field 'Event.address2'
        db.delete_column(u'events_event', 'address2')

        # Deleting field 'Event.hours'
        db.delete_column(u'events_event', 'hours')

        # Deleting field 'Event.extraeventtype'
        db.delete_column(u'events_event', 'extraeventtype')

        # Deleting field 'Event.stime'
        db.delete_column(u'events_event', 'stime')

        # Deleting field 'Event.address'
        db.delete_column(u'events_event', 'address')

        # Deleting field 'Event.donotshowartist'
        db.delete_column(u'events_event', 'donotshowartist')

        # Deleting field 'Event.displaytitle'
        db.delete_column(u'events_event', 'displaytitle')

        # Deleting field 'Event.phone'
        db.delete_column(u'events_event', 'phone')

        # Deleting field 'Event.country'
        db.delete_column(u'events_event', 'country')

        # Deleting field 'Event.locationlink'
        db.delete_column(u'events_event', 'locationlink')


    def backwards(self, orm):
        # Adding field 'Event.presenterfreeform'
        db.add_column(u'events_event', 'presenterfreeform',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Event.city'
        db.add_column(u'events_event', 'city',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Event.zip'
        db.add_column(u'events_event', 'zip',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Event.state'
        db.add_column(u'events_event', 'state',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Event.location'
        db.add_column(u'events_event', 'location',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Event.extrainformation'
        db.add_column(u'events_event', 'extrainformation',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Event.email'
        db.add_column(u'events_event', 'email',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Event.tickets'
        db.add_column(u'events_event', 'tickets',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Event.displaydescription'
        db.add_column(u'events_event', 'displaydescription',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Event.address2'
        db.add_column(u'events_event', 'address2',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Event.hours'
        db.add_column(u'events_event', 'hours',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Event.extraeventtype'
        db.add_column(u'events_event', 'extraeventtype',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Event.stime'
        db.add_column(u'events_event', 'stime',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Event.address'
        db.add_column(u'events_event', 'address',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Event.donotshowartist'
        db.add_column(u'events_event', 'donotshowartist',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Event.displaytitle'
        db.add_column(u'events_event', 'displaytitle',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Event.phone'
        db.add_column(u'events_event', 'phone',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Event.country'
        db.add_column(u'events_event', 'country',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Event.locationlink'
        db.add_column(u'events_event', 'locationlink',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


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
            'Meta': {'ordering': "['-startday']", 'object_name': 'Event'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'artists_playing': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['artists.Artist']", 'through': u"orm['events.GigPlayed']", 'symmetrical': 'False'}),
            'datefreeform': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'endday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'event_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.EventType']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'startday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
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