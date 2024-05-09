import logging

from artists.models import Artist, Instrument
from artists.models import ArtistEarnings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.db.models import Count
from events.models import GigPlayed
from oscar_apps.catalogue.models import ArtistProduct
from subscriptions.models import Donation

User = get_user_model()

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Clean up artist'

    def handle(self, *args, **options):
        logger.error("------ Entered the commend ------------")
        duplicate_artist_name = [
            'Joe Abba',
            'Shabnam Abedi',
            'Abdias Armenteros',
            'Elijah Balbed',
            'Or Bareket',
            'Farrid Baron',
            'Carl Bartlett, Jr',
            'Kahlil Bell',
            'Zwelakhe-Duma Bell le Pere',
            'Paolo Benedettini',
            'Pat Bianchi',
            'Johnathan Blake',
            'Steve Blum',
            'Peter Brainin',
            'Josh Breakstone',
            'Nic Cacioppo',
            'Niall Cade',
            'Haggai Cohen',
            'John Coltrane',
            'Tommy Crane',
            'George DeLancey',
            'Tom DiCarlo',
            'Phil Donkin',
            'Chris Donnelly',
            'Brian Drye',
            'Jovan Johnson',
            'Maya Keren',
            'Ian Macdonald',
            'Matt McDonald',
            'Dave Meder',
            'Hendrik Meurkens',
            'Anthony Nelson',
            'Tatiana Parra',
            'Valerie Pamorov',
            'Christophe Panzani',
            'Wallace Roney',
            'Michael Stephens',
            'Mark Taylor',
            'Katie Thiroux',
            'Dean Torrey',
            'Alex Toth',
            'Mark Whitfield',
            'David Williams',
            'Michael Wolff',
            'Vickie Yang-Piano',
            'Benjamin Young',
            'Samir Zarif',
            'Rodolfo Zanetti'
        ]

        prepared_artist_data = []

        for artist_name in duplicate_artist_name:
            max_gigs = -1
            max_artist = None

            name_split = artist_name.split(' ')
            first_name, last_name = name_split[0], ' '.join(name_split[1:])

            artist = Artist.objects.filter(
                first_name__icontains=first_name, last_name__icontains=last_name
            ).annotate(
                total_gig_played_count=Count('gigs_played')
            )

            print("=======================================")
            print(f"Artist name {artist_name}")

            for current_artist in artist:
                user_ids = User.objects.filter(artist=current_artist).values_list('id', flat=True)

                print(f"Artis ID {current_artist.id}")
                print(f"Artist slug {current_artist.slug}")
                print(f"{current_artist.id}-{current_artist.slug}")
                print(f"User id {user_ids}")
                print(f"Total gigs: {current_artist.total_gig_played_count}")
                if current_artist.total_gig_played_count >= max_gigs:
                    max_gigs = current_artist.total_gig_played_count
                    max_artist = current_artist

            replace_artist = artist.exclude(id=max_artist.id).values_list('id', flat=True)
            prepared_artist_data.append({
                'artist_name': artist_name,
                'id': max_artist.id,
                'replace_id': list(replace_artist),
                'total_max_gigs': max_gigs
            })
            print("=======================================")


        """
        GigPlayed
        ArtistProduct
        ArtistEarnings
        Donation
        """

        artist_to_be_deleted = []

        for current_data in prepared_artist_data:
            replace_id = current_data['id']

            for delete_id in current_data['replace_id']:
                try:
                    with transaction.atomic():
                        GigPlayed.objects.filter(artist_id=delete_id).update(artist_id=replace_id)
                        ArtistProduct.objects.filter(artist_id=delete_id).update(artist_id=replace_id)
                        Donation.objects.filter(artist_id=delete_id).update(artist_id=replace_id)
                        ArtistEarnings.objects.filter(artist_id=delete_id).update(artist_id=replace_id)

                        User.objects.filter(artist_id=delete_id).update(is_active=False, artist=None)
                        artist_instruments = Instrument.objects.filter(artists__id=delete_id)

                        # Update the artist ID for each instrument
                        for instrument in artist_instruments:
                            instrument.artists.remove(delete_id)
                            instrument.artists.add(replace_id)

                        artist_to_be_deleted.append(delete_id)

                except Exception as Err:
                    logger.error(str(Err), exc_info=True)
                    print(f"Could not delete artists {delete_id}")

        print(f"Artist delete ids {artist_to_be_deleted}")

        if artist_to_be_deleted:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM artists_artist WHERE id IN %s", [tuple(artist_to_be_deleted)])
            except Exception as e:
                print(e)


