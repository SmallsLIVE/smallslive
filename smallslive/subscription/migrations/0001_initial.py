# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Transaction'
        db.create_table(u'subscription_transaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('subscription', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subscription.Subscription'], null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.SmallsUser'], null=True, blank=True)),
            ('event', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=64, decimal_places=2, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal(u'subscription', ['Transaction'])

        # Adding model 'Subscription'
        db.create_table(u'subscription_subscription', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=64, decimal_places=2)),
            ('trial_period', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('trial_unit', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('recurrence_period', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('recurrence_unit', self.gf('django.db.models.fields.CharField')(max_length=5, null=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'])),
        ))
        db.send_create_signal(u'subscription', ['Subscription'])

        # Adding model 'UserSubscription'
        db.create_table(u'subscription_usersubscription', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.SmallsUser'])),
            ('subscription', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subscription.Subscription'])),
            ('expires', self.gf('django.db.models.fields.DateField')(default=datetime.date.today, null=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('cancelled', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'subscription', ['UserSubscription'])

        # Adding unique constraint on 'UserSubscription', fields ['user', 'subscription']
        db.create_unique(u'subscription_usersubscription', ['user_id', 'subscription_id'])

        # Adding model 'ExpressTransaction'
        db.create_table(u'subscription_expresstransaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('raw_request', self.gf('django.db.models.fields.TextField')(max_length=512)),
            ('raw_response', self.gf('django.db.models.fields.TextField')(max_length=512)),
            ('response_time', self.gf('django.db.models.fields.FloatField')()),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=8, null=True, blank=True)),
            ('ack', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('correlation_id', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('token', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('profile_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('profile_status', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('error_code', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('error_message', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal('subscription', ['ExpressTransaction'])


    def backwards(self, orm):
        # Removing unique constraint on 'UserSubscription', fields ['user', 'subscription']
        db.delete_unique(u'subscription_usersubscription', ['user_id', 'subscription_id'])

        # Deleting model 'Transaction'
        db.delete_table(u'subscription_transaction')

        # Deleting model 'Subscription'
        db.delete_table(u'subscription_subscription')

        # Deleting model 'UserSubscription'
        db.delete_table(u'subscription_usersubscription')

        # Deleting model 'ExpressTransaction'
        db.delete_table(u'subscription_expresstransaction')


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
        u'users.smallsuser': {
            'Meta': {'object_name': 'SmallsUser'},
            'accept_agreement': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'access_level': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'blank': 'True'}),
            'address_1': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'address_2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'login_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone_1': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'renewal_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'subscription_price': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'subscription.expresstransaction': {
            'Meta': {'ordering': "('-date_created',)", 'object_name': 'ExpressTransaction'},
            'ack': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'correlation_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'error_code': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'error_message': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'profile_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'profile_status': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'raw_request': ('django.db.models.fields.TextField', [], {'max_length': '512'}),
            'raw_response': ('django.db.models.fields.TextField', [], {'max_length': '512'}),
            'response_time': ('django.db.models.fields.FloatField', [], {}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        u'subscription.subscription': {
            'Meta': {'ordering': "('price', '-recurrence_period')", 'object_name': 'Subscription'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '64', 'decimal_places': '2'}),
            'recurrence_period': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'recurrence_unit': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True'}),
            'trial_period': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'trial_unit': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        u'subscription.transaction': {
            'Meta': {'ordering': "('-timestamp',)", 'object_name': 'Transaction'},
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'event': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['subscription.Subscription']", 'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.SmallsUser']", 'null': 'True', 'blank': 'True'})
        },
        u'subscription.usersubscription': {
            'Meta': {'unique_together': "(('user', 'subscription'),)", 'object_name': 'UserSubscription'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'cancelled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'expires': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['subscription.Subscription']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.SmallsUser']"})
        }
    }

    complete_apps = ['subscription']