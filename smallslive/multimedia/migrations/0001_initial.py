# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Media'
        db.create_table(u'multimedia_media', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_column='mediaName', blank=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255, db_column='mediaPath', blank=True)),
            ('media_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['multimedia.MediaType'], null=True, blank=True)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'multimedia', ['Media'])

        # Adding model 'MediaType'
        db.create_table(u'multimedia_mediatype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=255, db_column='mediaType')),
        ))
        db.send_create_signal(u'multimedia', ['MediaType'])


    def backwards(self, orm):
        # Deleting model 'Media'
        db.delete_table(u'multimedia_media')

        # Deleting model 'MediaType'
        db.delete_table(u'multimedia_mediatype')


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
        u'multimedia.mediatype': {
            'Meta': {'object_name': 'MediaType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_column': "'mediaType'"})
        }
    }

    complete_apps = ['multimedia']