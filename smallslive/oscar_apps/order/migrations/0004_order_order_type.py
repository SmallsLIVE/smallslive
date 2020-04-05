# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_auto_20181024_1555'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_type',
            field=models.CharField(default=b'regular', max_length=32, choices=[(b'gift', b'gift'), (b'regular', b'regular'), (b'ticket', b'ticket')]),
            preserve_default=True,
        ),
    ]
