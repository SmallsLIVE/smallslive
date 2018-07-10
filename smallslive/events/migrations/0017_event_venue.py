# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


# noinspection PyPep8Naming
def fill_smalls_venue(apps, schema_editor):
    Venue = apps.get_model('events', 'Venue')
    Event = apps.get_model('events', 'Event')

    smallsvenue, _ = Venue.objects.get_or_create(name='Smalls')
    Event.objects.all().update(venue=smallsvenue)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0016_auto_20150514_1418'),
    ]

    operations = [
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='event',
            name='venue',
            field=models.ForeignKey(blank=True, to='events.Venue', null=True),
            preserve_default=True,
        ),
        migrations.RunPython(fill_smalls_venue, noop)
    ]
