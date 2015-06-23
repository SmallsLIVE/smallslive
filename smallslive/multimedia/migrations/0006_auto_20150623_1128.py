# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0005_auto_20150622_0915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mediafile',
            name='format',
            field=models.CharField(max_length=4, editable=False, choices=[(b'mp3', b'mp3'), (b'flac', b'flac'), (b'wav', b'wav'), (b'ogg', b'ogg'), (b'mp4', b'mp4'), (b'mpg', b'mpg'), (b'avi', b'avi'), (b'mkv', b'mkv'), (b'mov', b'mov'), (b'mpeg', b'mpeg'), (b'flv', b'flv'), (b'm4v', b'm4v')]),
            preserve_default=True,
        ),
    ]
