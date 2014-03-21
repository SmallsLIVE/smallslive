# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'UserProfile'
        db.delete_table(u'users_userprofile')


    def backwards(self, orm):
        # Adding model 'UserProfile'
        db.create_table(u'users_userprofile', (
            ('subscription_price', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('user_company', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('certification', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('dba', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('registration', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('digest', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('download_limit', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('access_level', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('renewal_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('website', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('login_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('tax_id', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('meta1int', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('address_1', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('address_2', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('referral', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('ein', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('site_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('phone_2', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phone_1', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('years_in_business', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('reseller_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('company_name', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('membership_type', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('degree', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('postback_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='profile', unique=True, to=orm['auth.User'])),
            ('graduated', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('president', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('license', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('accept_agreement', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('workplace', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('user_company_description', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('profile_photo_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal(u'users', ['UserProfile'])


    models = {
        
    }

    complete_apps = ['users']