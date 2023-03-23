# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0015_currentpayoutperiod_current_total_seconds'),
    ]

    operations = [
        migrations.CreateModel(
            name='PastPayoutPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('period_start', models.DateField()),
                ('period_end', models.DateField()),
                ('total_seconds', models.BigIntegerField(default=0)),
                ('total_amount', models.DecimalField(default=0, max_digits=10, decimal_places=4)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='artistearnings',
            options={'ordering': ['-payout_period']},
        ),
        migrations.RemoveField(
            model_name='artistearnings',
            name='period_end',
        ),
        migrations.RemoveField(
            model_name='artistearnings',
            name='period_start',
        ),
        migrations.AddField(
            model_name='artistearnings',
            name='artist_ratio',
            field=models.DecimalField(default=0, max_digits=11, decimal_places=10),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='artistearnings',
            name='artist_seconds',
            field=models.BigIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='artistearnings',
            name='payout_period',
            field=models.ForeignKey(related_name='artist_earnings', on_delete=models.SET_NULL, default=0, to='artists.PastPayoutPeriod'),
            preserve_default=False,
        ),
    ]
