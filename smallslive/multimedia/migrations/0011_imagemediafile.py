# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0010_remove_mediafile_bucket_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageMediaFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('photo', models.ImageField(upload_to=b'user_photos', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
