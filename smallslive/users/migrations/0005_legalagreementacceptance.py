# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20150330_0800'),
    ]

    operations = [
        migrations.CreateModel(
            name='LegalAgreementAcceptance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(related_name='legal_agreement_acceptance',  on_delete=models.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
