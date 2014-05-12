# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Feature.site'
        db.delete_column(u'subscription_feature', 'site_id')

        # Adding M2M table for field site on 'Feature'
        m2m_table_name = db.shorten_name(u'subscription_feature_site')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('feature', models.ForeignKey(orm[u'subscription.feature'], null=False)),
            ('site', models.ForeignKey(orm[u'sites.site'], null=False))
        ))
        db.create_unique(m2m_table_name, ['feature_id', 'site_id'])

        # Deleting field 'Subscription.site'
        db.delete_column(u'subscription_subscription', 'site_id')

        # Adding M2M table for field site on 'Subscription'
        m2m_table_name = db.shorten_name(u'subscription_subscription_site')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('subscription', models.ForeignKey(orm[u'subscription.subscription'], null=False)),
            ('site', models.ForeignKey(orm[u'sites.site'], null=False))
        ))
        db.create_unique(m2m_table_name, ['subscription_id', 'site_id'])


    def backwards(self, orm):
        # Adding field 'Feature.site'
        db.add_column(u'subscription_feature', 'site',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['sites.Site']),
                      keep_default=False)

        # Removing M2M table for field site on 'Feature'
        db.delete_table(db.shorten_name(u'subscription_feature_site'))

        # Adding field 'Subscription.site'
        db.add_column(u'subscription_subscription', 'site',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['sites.Site']),
                      keep_default=False)

        # Removing M2M table for field site on 'Subscription'
        db.delete_table(db.shorten_name(u'subscription_subscription_site'))


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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
        u'subscription.feature': {
            'Meta': {'object_name': 'Feature'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'site': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sites.Site']", 'symmetrical': 'False'})
        },
        u'subscription.subscription': {
            'Meta': {'ordering': "('price', '-recurrence_period')", 'object_name': 'Subscription'},
            'best_choice': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '64', 'decimal_places': '2'}),
            'recurrence_period': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'recurrence_unit': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'site': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sites.Site']", 'symmetrical': 'False'}),
            'trial_period': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'trial_unit': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'})
        },
        u'subscription.subscriptionfeature': {
            'Meta': {'object_name': 'SubscriptionFeature'},
            'feature': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['subscription.Feature']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['subscription.Subscription']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'subscription.transaction': {
            'Meta': {'ordering': "('-timestamp',)", 'object_name': 'Transaction'},
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '64', 'decimal_places': '2', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'event': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['subscription.Subscription']", 'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'subscription.usersubscription': {
            'Meta': {'unique_together': "(('user', 'subscription'),)", 'object_name': 'UserSubscription'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'cancelled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'expires': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['subscription.Subscription']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['subscription']