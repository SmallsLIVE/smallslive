# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mediafile',
            name='size',
            field=models.IntegerField(default=0, help_text=b'File size in bytes'),
            preserve_default=True,
        ),
    ]
