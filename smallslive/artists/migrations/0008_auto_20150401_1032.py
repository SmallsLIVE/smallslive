# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0007_remove_artist_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artist',
            name='salutation',
            field=models.CharField(blank=True, max_length=255, choices=[(b'Mr.', b'Mr.'), (b'Mrs.', b'Mrs.'), (b'Ms.', b'Ms.')]),
            preserve_default=True,
        ),
    ]
