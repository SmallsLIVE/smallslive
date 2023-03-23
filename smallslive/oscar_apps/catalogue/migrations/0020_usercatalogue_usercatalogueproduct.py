# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalogue', '0019_auto_20190108_1611'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCatalogue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('has_full_catalogue_access', models.BooleanField(default=False)),
                ('user', models.ForeignKey(related_name='catalogue_access',  on_delete=models.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserCatalogueProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('product', models.ForeignKey(related_name='access',  on_delete=models.SET_NULL, to='catalogue.Product')),
                ('user', models.ForeignKey(related_name='product_access',  on_delete=models.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
