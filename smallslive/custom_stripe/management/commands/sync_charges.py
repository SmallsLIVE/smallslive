# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-03 02:27
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import datetime
import sys
import uuid

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.core import serializers
from django.db import migrations, models
from django.db.models.deletion import SET_NULL
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError
from django.utils import six
from django.utils.timezone import utc
import djstripe.fields
from stripe.error import InvalidRequestError
from tqdm import tqdm


DJSTRIPE_SUBSCRIBER_MODEL = getattr(settings, "DJSTRIPE_SUBSCRIBER_MODEL", settings.AUTH_USER_MODEL)

def sync_charges():
    # This is okay, since we're only doing a forward migration.
    from djstripe.models import Charge

    from djstripe.context_managers import stripe_temporary_api_version

    with stripe_temporary_api_version("2016-03-07"):
        if Charge.objects.count():
            print("syncing charges. This may take a while.")

            for charge in tqdm(Charge.objects.all(), desc="Sync", unit=" charges"):
                try:
                    Charge.sync_from_stripe_data(charge.api_retrieve())
                except InvalidRequestError as ire:
                    tqdm.write(
                        "There was an error while syncing charge ({charge_id}).".format(charge_id=charge.stripe_id))
                    tqdm.write(
                        "Exception is - {exception}".format(exception=ire.error))

            print("Charge sync complete.")


class Command(BaseCommand):
    help = 'djstripe sync charges data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting sync djstripe charges'))
        sync_charges()
        self.stdout.write(self.style.SUCCESS('Successfully synced djstripe charges'))