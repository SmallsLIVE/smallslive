# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Artist.photo'
        db.alter_column(u'artists_artist', 'photo', self.gf('django.db.models.fields.files.ImageField')(max_length=150))

    def backwards(self, orm):

        # Changing field 'Artist.photo'
        db.alter_column(u'artists_artist', 'photo', self.gf('django.db.models.fields.files.ImageField')(max_length=100))

    models = {
        u'artists.artist': {
            'Meta': {'ordering': "['last_name']", 'object_name': 'Artist'},
            'artist_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['artists.ArtistType']", 'null': 'True', 'blank': 'True'}),
            'biography': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '150', 'blank': 'True'}),
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