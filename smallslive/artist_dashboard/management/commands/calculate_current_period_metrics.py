from django.core.management.base import NoArgsCommand
from artist_dashboard.utils import update_current_period_metrics


class Command(NoArgsCommand):
    help = 'Imports the video recordings from S3 and assigns them to correct events'

    def handle_noargs(self, *args, **options):
        update_current_period_metrics()
