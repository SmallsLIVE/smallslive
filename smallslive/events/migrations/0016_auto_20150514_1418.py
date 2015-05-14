# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0015_recording_view_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recording',
            name='media_file',
            field=models.OneToOneField(related_name='recording', to='multimedia.MediaFile'),
            preserve_default=True,
        ),
    ]
