# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djstripe', '0004_auto_20180912_1357'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomPlan',
            fields=[
                ('plan_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='djstripe.Plan')),
            ],
            options={
                'abstract': False,
            },
            bases=('djstripe.plan',),
        ),
    ]
