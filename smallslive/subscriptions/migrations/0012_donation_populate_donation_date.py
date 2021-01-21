# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from django.db import models, migrations


def apply_dates(apps, schema_editor):
    # Set all past donations donation date to the original date
    donation_class = apps.get_model('subscriptions', 'Donation')
    for donation in donation_class.objects.all():
        donation.donation_date = donation.date.date()
        donation.save()


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0011_donation_donation_date'),
    ]

    operations = [
        migrations.RunPython(apply_dates),
    ]