# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0007_remove_artist_user'),
        ('users', '0005_legalagreementacceptance'),
    ]

    operations = [
        migrations.AddField(
            model_name='smallsuser',
            name='artist',
            field=models.OneToOneField(related_name='user',  on_delete=models.SET_NULL, null=True, blank=True, to='artists.Artist'),
            preserve_default=True,
        ),
    ]
