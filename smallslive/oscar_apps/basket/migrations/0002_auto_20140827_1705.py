# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0001_initial'),
        ('catalogue', '0001_initial'),
        ('basket', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='lineattribute',
            name='option',
            field=models.ForeignKey(verbose_name='Option',  on_delete=models.SET_NULL, to='catalogue.Option'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='line',
            name='basket',
            field=models.ForeignKey(verbose_name='Basket',  on_delete=models.SET_NULL, related_name='lines', to='basket.Basket'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='line',
            name='product',
            field=models.ForeignKey(verbose_name='Product',  on_delete=models.SET_NULL, related_name='basket_lines', to='catalogue.Product'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='line',
            name='stockrecord',
            field=models.ForeignKey(related_name='basket_lines',  on_delete=models.SET_NULL, to='partner.StockRecord'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='line',
            unique_together=set([('basket', 'line_reference')]),
        ),
        migrations.AddField(
            model_name='basket',
            name='owner',
            field=models.ForeignKey(verbose_name='Owner',  on_delete=models.SET_NULL, related_name='baskets', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
