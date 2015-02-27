# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.CharField(max_length=12, serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('date', models.DateTimeField()),
                ('content', models.TextField(blank=True)),
                ('link', models.URLField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
