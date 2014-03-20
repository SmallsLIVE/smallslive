# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Artist.templateid'
        db.delete_column(u'artists_artist', 'templateid')

        # Adding field 'Artist.photo'
        db.add_column(u'artists_artist', 'photo',
                      self.gf('django.db.models.fields.files.ImageField')(default='', max_length=100, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Artist.templateid'
        db.add_column(u'artists_artist', 'templateid',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Artist.photo'
        db.delete_column(u'artists_artist', 'photo')


    models = {
        u'artists.artist': {
            'Meta': {'ordering': "['last_name']", 'object_name': 'Artist'},
            'artist_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['artists.ArtistType']", 'null': 'True', 'blank': 'True'}),
            'biography': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'salutation': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'artists.artisttype': {
            'Meta': {'object_name': 'ArtistType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['artists']