import os
from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.utils import timezone
from mailchimp import Mailchimp
from newsletters.models import Newsletter


class Command(NoArgsCommand):
    help = 'Fetch the newsletters from MailChimp'

    def handle_noargs(self, *args, **options):
        env = os.environ.get('CRON_ENV')
        now = timezone.now()
        # heroku scheduler launches the task every day, we make sure it only really does the import
        # once a week (tuesday)
        if env == "heroku" and now.weekday() != 1:
            return

        mc = Mailchimp(settings.MAILCHIMP_API_KEY)
        campaigns = mc.campaigns.list(filters={
            'status': 'sent',
            'title': 'SmallsLIVE',
            'exact': False}, limit=1000)
        for campaign in campaigns.get('data'):
            if not Newsletter.objects.filter(id=campaign.get('id')).exists():
                newsletter = Newsletter.objects.create(
                    id=campaign.get('id'),
                    title=campaign.get('title'),
                    date=campaign.get('send_time'),
                    link=campaign.get('archive_url')
                )
