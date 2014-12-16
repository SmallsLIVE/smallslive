# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('salutation', models.CharField(max_length=255, blank=True)),
                ('biography', tinymce.models.HTMLField(blank=True)),
                ('website', models.CharField(max_length=255, blank=True)),
                ('photo', models.ImageField(max_length=150, upload_to=b'artist_images', blank=True)),
            ],
            options={
                'ordering': ['last_name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Instrument',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('abbreviation', models.CharField(max_length=10, blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='artist',
            name='instruments',
            field=sortedm2m.fields.SortedManyToManyField(help_text=None, to='artists.Instrument', blank=True),
            preserve_default=True,
        ),
    ]
