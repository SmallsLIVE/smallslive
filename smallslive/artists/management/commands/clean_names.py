from django.core.management.base import NoArgsCommand

from artists.models import Artist


class Command(NoArgsCommand):
    help = 'Clean up artist names'

    def handle_noargs(self, *args, **options):
        """
        Artist index in 'Archive' is sorted by last name.
        Ensure there's always a last name, and remove first name
        if necessary.
        """
        for artist in Artist.objects.all():
            modified = False
            # Some last names are '.'. Clean that up.
            if artist.last_name is not None:
                artist.last_name = artist.last_name.strip(' .')
                modified = True

            if not artist.last_name:
                # swap values and strip.
                artist.last_name = artist.first_name.strip()
                artist.first_name = ''
                modified = True

            if modified:
                artist.save()
