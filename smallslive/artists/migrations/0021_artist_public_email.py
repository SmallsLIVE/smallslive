# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0020_auto_20180924_2117'),
    ]

    operations = [
        migrations.AddField(
            model_name='artist',
            name='public_email',
            field=models.EmailField(max_length=75, null=True, blank=True),
            preserve_default=True,
        ),
        # migrations.RunSQL(
        #     # @TODO : Fix later
        #     # 'UPDATE artists_artist AS A SET public_email=U.email FROM users_smallsuser as U WHERE U.artist_id=A.id;',
        #     # 'UPDATE artists_artist set public_email=null;'
        # )
    ]
