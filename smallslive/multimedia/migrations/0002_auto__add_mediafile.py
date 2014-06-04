# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MediaFile'
        db.create_table(u'multimedia_mediafile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('media_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('format', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('file', self.gf('multimedia.fields.DynamicBucketFileField')(max_length=100)),
        ))
        db.send_create_signal(u'multimedia', ['MediaFile'])


    def backwards(self, orm):
        # Deleting model 'MediaFile'
        db.delete_table(u'multimedia_mediafile')


    models = {
        u'multimedia.media': {
            'Meta': {'object_name': 'Media'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['multimedia.MediaType']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "'mediaName'", 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "'mediaPath'", 'blank': 'True'})
        },
        u'multimedia.mediafile': {
            'Meta': {'object_name': 'MediaFile'},
            'file': ('multimedia.fields.DynamicBucketFileField', [], {'max_length': '100'}),
            'format': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'multimedia.mediatype': {
            'Meta': {'object_name': 'MediaType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "'mediaType'"})
        }
    }

    complete_apps = ['multimedia']