# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0009_mediafile_bucket_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mediafile',
            name='bucket_name',
        ),
    ]
