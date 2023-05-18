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



def resync_subscriptions():
    """
    Since subscription IDs were not previously stored, a direct migration will leave us
    with a bunch of orphaned objects. It was decided [here](https://github.com/kavdev/dj-stripe/issues/162)
    that a purge and re-sync would be the best option. No data that is currently available on stripe will
    be deleted. Anything stored locally will be purged.
    """

    # This is okay, since we're only doing a forward migration.
    from djstripe.models import Subscription

    from djstripe.context_managers import stripe_temporary_api_version

    with stripe_temporary_api_version("2016-03-07"):
        if Subscription.objects.count():
            # print("Purging subscriptions. Don't worry, all active subscriptions will be re-synced from stripe. Just in \
            # case you didn't get the memo, we'll print out a json representation of each object for your records:")
            # print(serializers.serialize("json", Subscription.objects.all()))
            Subscription.objects.all().delete()

            print("Re-syncing subscriptions. This may take a while.")

            for stripe_subscription in tqdm(iterable=Subscription.api_list(), desc="Sync", unit=" subscriptions"):
                subscription = Subscription.sync_from_stripe_data(stripe_subscription)

                if not subscription.customer:
                    tqdm.write("The customer for this subscription ({subscription_id}) does not exist locally (so we \
                    won't sync the subscription). You'll want to figure out how that \
                    happened.".format(subscription_id=stripe_subscription['id']))

            print("Subscription re-sync complete.")


class Command(BaseCommand):
    help = 'djstripe resync subscription data'

    def handle(self, *args, **options):
            self.stdout.write(self.style.SUCCESS('Starting resync subscriptions'))
            resync_subscriptions()
            self.stdout.write(self.style.SUCCESS('Successfully resynced djstripe subscriptions'))