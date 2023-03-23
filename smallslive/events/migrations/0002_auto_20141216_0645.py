# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0002_artist_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='last_modified_by',
            field=models.ForeignKey(blank=True, on_delete=models.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='performers',
            field=models.ManyToManyField(related_name='events', through='events.GigPlayed', to='artists.Artist'),
            preserve_default=True,
        ),
    ]
