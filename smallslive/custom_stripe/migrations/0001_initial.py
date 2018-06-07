# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StripePlan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stripe_id', models.CharField(unique=True, max_length=50)),
                ('nickname', models.CharField(max_length=100)),
                ('amount', models.IntegerField()),
                ('interval', models.CharField(max_length=10, verbose_name=b'Interval type', choices=[('week', 'Week'), ('month', 'Month'), ('year', 'Year')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
