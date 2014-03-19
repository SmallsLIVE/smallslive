# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Artist'
        db.create_table(u'artists_artist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('firstname', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('lastname', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('salutation', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('artist_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['artists.ArtistType'], null=True, blank=True)),
            ('biography', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('templateid', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('website', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'artists', ['Artist'])

        # Adding model 'ArtistType'
        db.create_table(u'artists_artisttype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'artists', ['ArtistType'])


    def backwards(self, orm):
        # Deleting model 'Artist'
        db.delete_table(u'artists_artist')

        # Deleting model 'ArtistType'
        db.delete_table(u'artists_artisttype')


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
        }
    }

    complete_apps = ['artists']