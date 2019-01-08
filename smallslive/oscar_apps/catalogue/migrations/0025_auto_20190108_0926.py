# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0021_artist_public_email'),
        ('catalogue', '0024_auto_20190108_0917'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArtistProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('artist', models.ForeignKey(verbose_name=b'', to='artists.Artist')),
                ('product', models.ForeignKey(verbose_name=b'', to='catalogue.Product')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='product',
            name='artist',
        ),
        migrations.AddField(
            model_name='product',
            name='artist',
            field=models.ManyToManyField(to='artists.Artist', null=True, verbose_name=b'Attributes', through='catalogue.ArtistProduct', blank=True),
            preserve_default=True,
        ),
    ]
