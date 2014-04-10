# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    depends_on = (
        ('artists', '0001_initial'),
    )

    def forwards(self, orm):
        # Adding model 'Event'
        db.create_table(u'events_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('startday', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('endday', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('stime', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('subtitle', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('address2', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('event_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.EventType'], null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('displaytitle', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('displaydescription', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('extrainformation', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('donotshowartist', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('locationlink', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('tickets', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('hours', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('datefreeform', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('presenterfreeform', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('extraeventtype', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'events', ['Event'])

        # Adding model 'EventType'
        db.create_table(u'events_eventtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('parent', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'events', ['EventType'])

        # Adding model 'GigPlayed'
        db.create_table(u'events_gigplayed', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(related_name='gigs_played', to=orm['artists.Artist'])),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(related_name='artists_gig_info', to=orm['events.Event'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['artists.ArtistType'])),
            ('sort_order', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
        ))
        db.send_create_signal(u'events', ['GigPlayed'])


    def backwards(self, orm):
        # Deleting model 'Event'
        db.delete_table(u'events_event')

        # Deleting model 'EventType'
        db.delete_table(u'events_eventtype')

        # Deleting model 'GigPlayed'
        db.delete_table(u'events_gigplayed')


    models = {
        u'artists.artist': {
            'Meta': {'object_name': 'Artist'},
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
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'artists_playing': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['artists.Artist']", 'through': u"orm['events.GigPlayed']", 'symmetrical': 'False'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'datefreeform': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'displaydescription': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'displaytitle': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'donotshowartist': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'endday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'event_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.EventType']", 'null': 'True', 'blank': 'True'}),
            'extraeventtype': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'extrainformation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'hours': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'locationlink': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'presenterfreeform': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'startday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'stime': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'subtitle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'tickets': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
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