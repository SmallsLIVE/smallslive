# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import tinymce.models
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0001_initial'),
        ('artists', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('title', models.CharField(max_length=255)),
                ('start', models.DateTimeField(null=True, blank=True)),
                ('end', models.DateTimeField(null=True, blank=True)),
                ('set', models.CharField(blank=True, max_length=10, choices=[(b'22:00-23:00', b'10-11pm'), (b'23:00-0:00', b'11-12pm'), (b'0:00-1:00', b'12-1am')])),
                ('description', tinymce.models.HTMLField(blank=True)),
                ('subtitle', models.CharField(max_length=255, blank=True)),
                ('link', models.CharField(max_length=255, blank=True)),
                ('active', models.BooleanField(default=False)),
                ('date_freeform', models.TextField(blank=True)),
                ('photo', models.ImageField(max_length=150, upload_to=b'event_images', blank=True)),
                ('state', model_utils.fields.StatusField(default=b'Draft', max_length=100, no_check_for_status=True, choices=[(b'Published', b'Published'), (b'Draft', b'Draft'), (b'Cancelled', b'Cancelled'), (b'Hidden', b'Hidden')])),
            ],
            options={
                'ordering': ['-start'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('parent', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GigPlayed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_leader', models.BooleanField(default=False)),
                ('sort_order', models.CharField(max_length=30, blank=True)),
                ('artist', models.ForeignKey(related_name='gigs_played',  on_delete=models.SET_NULL, to='artists.Artist')),
                ('event', models.ForeignKey(related_name='artists_gig_info',  on_delete=models.SET_NULL, to='events.Event')),
                ('role', models.ForeignKey(to='artists.Instrument',  on_delete=models.SET_NULL)),
            ],
            options={
                'ordering': ['event', 'sort_order', 'is_leader'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Set',
            fields=[
                ('media_file', models.OneToOneField(related_name='set',  on_delete=models.SET_NULL, primary_key=True, serialize=False, to='multimedia.MediaFile')),
                ('set_number', models.IntegerField(default=1)),
                ('event', models.ForeignKey(related_name='sets',  on_delete=models.SET_NULL, to='events.Event')),
            ],
            options={
                'ordering': ['set_number'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='event',
            name='event_type',
            field=models.ForeignKey(blank=True,  on_delete=models.SET_NULL, to='events.EventType', null=True),
            preserve_default=True,
        ),
    ]
