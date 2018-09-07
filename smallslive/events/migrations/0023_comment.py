# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0022_event_tickets_url_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id',
                    models.AutoField(verbose_name='ID',
                    serialize=False,
                    auto_created=True,
                    primary_key=True)),
                ('status',
                    models.CharField(
                        default=b'A',
                        max_length=2,
                        choices=[(b'A', b'Approved'),
                                 (b'R', b'Rejected'),
                                 (b'IR', b'In Review')])),
                ('created_at', models.DateTimeField()),
                ('content', models.TextField(max_length=500, null=True)),
                ('author', models.ForeignKey(
                    related_name='comments',
                    to=settings.AUTH_USER_MODEL)),
                ('event_set', models.ForeignKey(
                    related_name='comments',
                    to='events.EventSet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
