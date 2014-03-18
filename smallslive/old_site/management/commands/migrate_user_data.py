import json
import pytz
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils import timezone
from users.models import UserProfile


class Command(BaseCommand):
    args = '<user_data.json>'
    help = 'Imports user data from the JSON file'

    def handle(self, *args, **options):
        if args[0]:
            json_file = json.load(open(args[0], 'r'))
        else:
            raise CommandError('Provide the path to JSON file as an argument to this command')

        columns = json_file['QUERY']['COLUMNS']
        count = 0
        for user in json_file['QUERY']['DATA']:
            # Import or create users
            user_data = dict(zip(columns, user))
            try:
                user = User.objects.get(username=str(user_data['NAME'])[:30])
            except User.DoesNotExist:
                user = User.objects.create(
                    id=user_data['USERID'],
                    username=str(user_data['NAME'])[:30],
                    email=str(user_data['EMAIL']),
                    password=str(user_data['PASS']),
                    first_name=str(user_data['FIRSTNAME']),
                    last_name=str(user_data['LASTNAME']),
                )
                count += 1

            # Import user profile data
            profile, created = UserProfile.objects.get_or_create(user=user)

            profile.accept_agreement = user_data['ACCEPTAGREEMENT']
            profile.access_level = user_data['ACCESSLEVEL']
            profile.active = user_data['ACTIVE']
            profile.address_1 = user_data['ADDRESS1'] or ""
            profile.address_2 = user_data['ADDRESS2'] or ""
            profile.certification = user_data['CERTIFICATION'] or ""
            profile.city = user_data['CITY'] or ""
            profile.company_id = user_data['COMPANYID']
            profile.company_name = user_data['COMPANYNAME']
            profile.country = user_data['COUNTRY'] or ""
            profile.dba = user_data['DBA'] or ""
            profile.degree = user_data['DEGREE'] or ""
            profile.digest = user_data['DIGEST'] or ""
            profile.download_limit = user_data['DOWNLOADLIMIT']
            profile.ein = user_data['EIN'] or ""
            profile.fax = user_data['FAX'] or ""
            profile.graduated = user_data['GRADUATED'] or ""
            profile.last_login = self.parse_date(user_data['LASTLOGIN'])
            profile.license = user_data['LICENSE'] or ""
            profile.location = user_data['LOCATION'] or ""
            profile.login_count = user_data['LOGINCOUNT']
            profile.membership_type = user_data['MEMBERSHIPTYPE'] or ""
            profile.meta1int = user_data['META1INT']
            profile.phone_1 = user_data['PHONE1'] or ""
            profile.phone_2 = user_data['PHONE2'] or ""
            profile.postback_date = user_data['POSTBACKDATE']
            profile.president = user_data['PRESIDENT'] or ""
            profile.profile_photo_id = user_data['PROFILEPHOTOID']
            profile.referral = user_data['REFERRAL'] or ""
            profile.registration = user_data['REGISTRATION'] or ""
            profile.renewal_date = self.parse_date(user_data['RENEWALDATE'])
            profile.reseller_id = user_data['RESELLERID']
            profile.site_id = user_data['SITEID']
            profile.start_date = self.parse_date(user_data['STARTDATE'])
            profile.state = user_data['STATE'] or ""
            profile.subscription_price = user_data['SUBSCRIPTIONPRICE'] or 0
            profile.tax_id = user_data['TAXID'] or ""
            profile.title = user_data['TITLE'] or ""
            profile.type = user_data['TYPE'] or ""
            profile.user_company = user_data['USERCOMPANY'] or ""
            profile.user_company_description = user_data['USERCOMPANYDESCRIPTION'] or ""
            profile.website = user_data['WEBSITE'] or ""
            profile.workplace = user_data['WORKPLACE'] or ""
            profile.years_in_business = user_data['YEARSINBUSINESS']
            profile.zip = user_data['ZIP'] or ""
            profile.save()

        self.stdout.write('Successfully imported {0} users'.format(count))

    def parse_date(self, date_string):
        if date_string:
            date = datetime.strptime(date_string, "%B, %d %Y %H:%M:%S")
            date = pytz.timezone(timezone.get_default_timezone_name()).localize(date, is_dst=False)
        else:
            date = None
        return date