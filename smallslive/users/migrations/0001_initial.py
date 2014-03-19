# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserProfile'
        db.create_table(u'users_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='profile', unique=True, to=orm['auth.User'])),
            ('access_level', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('reseller_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('site_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('login_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('accept_agreement', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('download_limit', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('start_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('renewal_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('subscription_price', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('company_name', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('address_1', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('address_2', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('phone_1', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('phone_2', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('website', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('meta1int', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('user_company', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('user_company_description', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('digest', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('referral', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('degree', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('graduated', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('membership_type', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('postback_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('profile_photo_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('workplace', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('years_in_business', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('dba', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('tax_id', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('ein', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('president', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('license', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('certification', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('registration', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'users', ['UserProfile'])


    def backwards(self, orm):
        # Deleting model 'UserProfile'
        db.delete_table(u'users_userprofile')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'users.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'accept_agreement': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'access_level': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'address_1': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'address_2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'certification': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'dba': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'degree': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'digest': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'download_limit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ein': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'graduated': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'license': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'login_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'membership_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'meta1int': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'phone_1': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'phone_2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'postback_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'president': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'profile_photo_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'referral': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'registration': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'renewal_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'reseller_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'site_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'subscription_price': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'tax_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'profile'", 'unique': 'True', 'to': u"orm['auth.User']"}),
            'user_company': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user_company_description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'workplace': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'years_in_business': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['users']