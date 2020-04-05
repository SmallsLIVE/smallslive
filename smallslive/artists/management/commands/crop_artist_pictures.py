from django.core.management.base import NoArgsCommand

from artists.models import Artist
from artists.helpers import crop_artist_pictures


class Command(NoArgsCommand):
    help = 'Rebuild artists cropping boxes'

    def handle_noargs(self, *args, **options):
        crop_artist_pictures(Artist.objects.all())
