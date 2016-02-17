# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0013_auto_20160217_0850'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrentPayoutPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('period_start', models.DateField()),
                ('period_end', models.DateField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
