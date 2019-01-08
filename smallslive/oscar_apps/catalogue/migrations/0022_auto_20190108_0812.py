# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0021_artist_public_email'),
        ('catalogue', '0021_auto_20190108_0811'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='artist_list',
            field=models.ManyToManyField(to='artists.Artist', null=True, verbose_name=b'Attributes', blank=True),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='product',
            name='artist',
        ),
        migrations.AddField(
            model_name='product',
            name='artist',
            field=models.ForeignKey(related_name='artist', blank=True, to='artists.Artist', null=True),
            preserve_default=True,
        ),
    ]

