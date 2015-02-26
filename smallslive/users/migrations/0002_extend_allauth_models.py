# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('account', '__first__'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SmallsEmailAddress',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('account.emailaddress',),
        ),
        migrations.CreateModel(
            name='SmallsEmailConfirmation',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('account.emailconfirmation',),
        ),
    ]
