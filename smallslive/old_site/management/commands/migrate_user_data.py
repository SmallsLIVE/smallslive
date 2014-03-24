import json
import pytz
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    args = '<user_data.json> <hash_passwords>'
    help = 'Imports user data from the JSON file'

    def handle(self, *args, **options):
        if args[0]:
            json_file = json.load(open(args[0], 'r'))
        else:
            raise CommandError('Provide the path to JSON file as an argument to this command')

        hash_pass = True
        if len(args) == 2 and args[1] == 'false':
            hash_pass = False

        columns = json_file['QUERY']['COLUMNS']
        count = 0
        for user in json_file['QUERY']['DATA']:
            # Convert to unicode and strip whitespace only on string values
            user = [unicode(v).strip() if isinstance(v, str) else v for v in user]
            user_data = dict(zip(columns, user))
            # Convert email to lowercase and convert to unicode in case it's not string data
            email = User.objects.normalize_email(unicode(user_data['NAME']))
            if not email:
                continue
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                if hash_pass:
                    user = User.objects.create_user(
                        email,
                        password=user_data['PASS'],
                        id=user_data['USERID'],
                        first_name=user_data['FIRSTNAME'] if user_data['FIRSTNAME'] else "",
                        last_name=user_data['LASTNAME'] if user_data['LASTNAME'] else "",
                    )
                else:
                    user = User.objects.create(
                        email=email,
                        password=user_data['PASS'],
                        id=user_data['USERID'],
                        first_name=user_data['FIRSTNAME'] if user_data['FIRSTNAME'] else "",
                        last_name=user_data['LASTNAME'] if user_data['LASTNAME'] else "",
                    )
                count += 1

            user.accept_agreement = user_data['ACCEPTAGREEMENT']
            user.access_level = user_data['ACCESSLEVEL']
            user.is_active = user_data['ACTIVE']
            user.address_1 = user_data['ADDRESS1'] or ""
            user.address_2 = user_data['ADDRESS2'] or ""
            user.city = user_data['CITY'] or ""
            user.company_name = user_data['COMPANYNAME']
            user.country = user_data['COUNTRY'] or ""
            user.date_joined = self.parse_date(user_data['STARTDATE'])
            user.last_login = self.parse_date(user_data['LASTLOGIN'], null=False)
            user.login_count = user_data['LOGINCOUNT']
            user.phone_1 = user_data['PHONE1'] or ""
            user.renewal_date = self.parse_date(user_data['RENEWALDATE'])
            user.state = user_data['STATE'] or ""
            user.subscription_price = user_data['SUBSCRIPTIONPRICE'] or 0
            user.website = user_data['WEBSITE'] or ""
            user.zip = user_data['ZIP'] or ""
            user.save()

        self.stdout.write('Successfully imported {0} users'.format(count))

    def parse_date(self, date_string, null=True):
        if date_string:
            date = datetime.strptime(date_string, "%B, %d %Y %H:%M:%S")
            date = pytz.timezone(timezone.get_default_timezone_name()).localize(date, is_dst=False)
        elif null is False:
            # For fields that don't allow null values, set to epoch
            date = datetime.utcfromtimestamp(0)
            date = pytz.timezone(timezone.get_default_timezone_name()).localize(date, is_dst=False)
        else:
            date = None
        return date