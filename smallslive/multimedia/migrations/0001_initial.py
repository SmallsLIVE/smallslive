# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multimedia.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, db_column=b'mediaName', blank=True)),
                ('path', models.CharField(max_length=255, db_column=b'mediaPath', blank=True)),
                ('filename', models.CharField(max_length=255, blank=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MediaFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('media_type', models.CharField(max_length=10, editable=False, choices=[(b'video', b'video'), (b'audio', b'audio')])),
                ('format', models.CharField(max_length=4, editable=False, choices=[(b'mp3', b'mp3'), (b'flac', b'flac'), (b'wav', b'wav'), (b'mp4', b'mp4'), (b'mpg', b'mpg'), (b'avi', b'avi'), (b'mkv', b'mkv'), (b'mov', b'mov'), (b'mpeg', b'mpeg'), (b'flv', b'flv'), (b'm4v', b'm4v')])),
                ('file', multimedia.fields.DynamicBucketFileField(upload_to=b'/')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MediaType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=255, db_column=b'mediaType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='media',
            name='media_type',
            field=models.ForeignKey(blank=True,  on_delete=models.SET_NULL, to='multimedia.MediaType', null=True),
            preserve_default=True,
        ),
    ]
