# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('currency', models.CharField(default=b'USD', max_length=12)),
                ('amount', models.DecimalField(default=Decimal('0.00'), max_digits=12, decimal_places=2)),
                ('payment_source', models.CharField(max_length=64)),
                ('reference', models.CharField(max_length=128, blank=True)),
                ('label', models.CharField(max_length=128, blank=True)),
                ('user', models.ForeignKey(related_name='donations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
