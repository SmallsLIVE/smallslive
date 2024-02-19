from django.core.management.base import BaseCommand
from artist_dashboard.utils import update_current_period_metrics


class Command(BaseCommand):
    help = 'Imports the video recordings from S3 and assigns them to correct events'

    def handle(self, *args, **options):
        update_current_period_metrics()
