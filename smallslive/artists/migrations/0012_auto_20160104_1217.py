# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import artists.models


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0011_auto_20150804_1553'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArtistEarnings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('period_start', models.DateField()),
                ('period_end', models.DateField()),
                ('amount', models.DecimalField(default=0, max_digits=10, decimal_places=4)),
                ('artist', models.ForeignKey(related_name='earnings', on_delete=models.SET_NULL,  to='artists.Artist')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='artist',
            name='photo',
            field=models.ImageField(max_length=150, upload_to=artists.models.artist_image_path, blank=True),
            preserve_default=True,
        ),
    ]
