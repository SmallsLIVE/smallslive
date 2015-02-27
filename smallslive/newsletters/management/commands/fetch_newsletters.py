from django.conf import settings
from django.core.management.base import NoArgsCommand
from mailchimp import Mailchimp
from newsletters.models import Newsletter


class Command(NoArgsCommand):
    help = 'Fetch the newsletters from MailChimp'

    def handle_noargs(self, *args, **options):
        mc = Mailchimp(settings.MAILCHIMP_API_KEY)
        campaigns = mc.campaigns.list(filters={'status': 'sent'})
        for campaign in campaigns.get('data', ):
            if not Newsletter.objects.filter(id=campaign.get('id')).exists():
                newsletter = Newsletter.objects.create(
                    id=campaign.get('id'),
                    title=campaign.get('title'),
                    date=campaign.get('send_time'),
                    link=campaign.get('archive_url')
                )
                content = mc.campaigns.content(campaign.get('id'))
                newsletter.content = content.get('text', '')
                newsletter.save()
