# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_smallsuser_newsletter'),
    ]

    operations = [
        migrations.AddField(
            model_name='smallsuser',
            name='payout_method',
            field=models.CharField(default=b'Check', max_length=10, choices=[(b'Check', b'Check'), (b'PayPal', b'PayPal')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='smallsuser',
            name='paypal_email',
            field=models.EmailField(max_length=100, blank=True),
            preserve_default=True,
        ),
    ]
