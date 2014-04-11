import csv
import json
import pytz
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from artists.models import Artist

User = get_user_model()


class Command(BaseCommand):
    args = '<user_data.csv>'
    help = 'Imports user data from the csv file'

    def handle(self, *args, **options):
        if args[0]:
            csv_file = csv.DictReader(open(args[0], 'rU'))
        else:
            raise CommandError('Provide the path to csv file as an argument to this command')

        created_count = 0
        total_count = 0
        for user_data in csv_file:
            # Convert to unicode and strip whitespace only on string values
            for key, val in user_data.items():
                if isinstance(user_data[key], str):
                    user_data[key] = unicode(val.decode('utf-8')).strip()
            # Convert email to lowercase and convert to unicode in case it's not string data
            email = User.objects.normalize_email(user_data['name'])
            print email
            if not email:
                continue
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = User.objects.create_user(
                    email,
                    id=user_data['userId'],
                    first_name=user_data['firstname'],
                )

                created_count += 1

            #user.accept_agreement = user_data['ACCEPTAGREEMENT']
            user.access_level = user_data['accesslevel']
            #user.is_active = user_data['ACTIVE']
            user.address_1 = user_data['address1']
            user.address_2 = user_data['address2']
            user.city = user_data['city']
            #user.company_name = user_data['COMPANYNAME']
            user.country = user_data['country']
            user.date_joined = self.parse_date(user_data['startDate'])
            user.last_login = self.parse_date(user_data['lastLogin'], null=False)
            user.login_count = user_data['logincount']
            user.phone_1 = user_data['phone1']
            user.renewal_date = self.parse_date(user_data['renewalDate'])
            user.state = user_data['state']
            user.subscription_price = int(float(user_data['subscriptionPrice'])) if user_data['subscriptionPrice'] else 0
            user.website = user_data['website']
            user.zip = user_data['zip']
            user.save()

            # Connect artist to user
            artist_id = user_data['meta1Int']
            if artist_id:
                try:
                    artist = Artist.objects.get(id=artist_id)
                    artist.user = user
                    artist.save()
                except Artist.DoesNotExist:
                    pass

            # Output to console so that the user can see something's happening
            total_count += 1
            if total_count % 500 == 0:
                self.stdout.write('Successfully checked {0} users'.format(total_count))

        self.stdout.write('Successfully imported {0} users'.format(created_count))

    def parse_date(self, date_string, null=True):
        if date_string:
            date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S.%f")
            date = pytz.timezone(timezone.get_default_timezone_name()).localize(date, is_dst=False)
        elif null is False:
            # For fields that don't allow null values, set to epoch
            date = datetime.utcfromtimestamp(0)
            date = pytz.timezone(timezone.get_default_timezone_name()).localize(date, is_dst=False)
        else:
            date = None
        return date