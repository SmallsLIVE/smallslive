import bleach
from bs4 import BeautifulSoup
from django.core.management.base import NoArgsCommand

from artists.models import Artist, ArtistType
from events.models import Event, EventType, GigPlayed
from multimedia.models import MediaType, Media
from old_site.models import Joinmediaevent, Joinmediaperson,Joinpersonevent, OldEvent,\
    OldEventTypes, OldPerson, OldPersonType, OldMedia, OldMediaType


class Command(NoArgsCommand):
    help = 'Migrates the data from the old site to new models'

    def clean_up_html(self, text):
        allowed_tags = ['a', 'p']

        # remove all tags except allowed tags
        cleaned_up_html = bleach.clean(text, tags=allowed_tags, strip=True)

        # remove empty paragraph tags
        soup = BeautifulSoup(cleaned_up_html, 'html.parser')
        for p in soup.find_all('p'):
            if not p.text.strip():
                p.decompose()

        return unicode(soup)

    def migrate_artists(self):
        # Artist types
        count = 0
        for old_person_type in OldPersonType.objects.using('old').all():
            artist_type, created = ArtistType.objects.get_or_create(
                id=old_person_type.persontypeid,
                name=old_person_type.persontype
            )
            if created:
                count += 1
        self.stdout.write('Successfully imported {0} artist types'.format(count))

        # Artists
        count = 0
        for old_artist in OldPerson.objects.using('old').all():
            new_artist, artist_created = Artist.objects.get_or_create(id=old_artist.personid)

            # Regular fields
            new_artist.biography = self.clean_up_html(old_artist.biography)
            new_artist.first_name = old_artist.firstname
            new_artist.last_name = old_artist.lastname
            new_artist.salutation = old_artist.salutation
            new_artist.website = old_artist.website or ""

            # Foreign keys
            artist_type, artist_type_created = ArtistType.objects.get_or_create(
                id=old_artist.persontypeid_id,
                name=old_artist.persontypeid.persontype,
            )
            new_artist.artist_type = artist_type

            if artist_created:
                count += 1

            new_artist.save()
        self.stdout.write('Successfully imported {0} artists'.format(count))

    def migrate_events(self):
        # Event types
        count = 0
        for old_event_type in OldEventTypes.objects.using('old').all():
            new_event_type, created = EventType.objects.get_or_create(
                id=old_event_type.eventtypeid,
                name=old_event_type.eventtype,
                parent=old_event_type.eventtypeparent
            )
            if created:
                count += 1
        self.stdout.write('Successfully imported {0} event types'.format(count))

        # Events
        count = 0
        for old_event in OldEvent.objects.using('old').all():
            new_event, event_created = Event.objects.get_or_create(id=old_event.eventid)

            # Regular fields
            new_event.active = old_event.active
            new_event.date_freeform = old_event.datefreeform
            new_event.description = old_event.description
            new_event.email = old_event.email
            new_event.end_day = old_event.endday
            new_event.link = old_event.link
            new_event.start_day = old_event.startday
            new_event.subtitle = old_event.subtitle
            new_event.title = old_event.title

            # Foreign keys
            event_type, event_type_created = EventType.objects.get_or_create(
                id=old_event.eventtype_id,
                name=old_event.eventtype.eventtype,
                parent=old_event.eventtype.eventtypeparent
            )
            new_event.event_type = event_type

            if event_created:
                count += 1

            new_event.save()
        self.stdout.write('Successfully imported {0} events'.format(count))

    def migrate_media(self):
        # Media types
        count = 0
        for old_media_type in OldMediaType.objects.using('old').all():
            new_media_type, created = MediaType.objects.get_or_create(
                id=old_media_type.mediatypeid,
                type=old_media_type.mediatype,
            )
            if created:
                count += 1
        self.stdout.write('Successfully imported {0} media types'.format(count))

        # Media
        count = 0
        for old_media in OldMedia.objects.using('old').all():
            new_media, media_created = Media.objects.get_or_create(id=old_media.mediaid)
            if media_created:
                count += 1

            # Regular fields
            new_media.description = old_media.description or ""
            new_media.filename = old_media.filename or ""
            new_media.name = old_media.medianame or ""
            new_media.path = old_media.mediapath or ""

            # Foreign keys
            new_media.media_type_id = old_media.mediatypeid

            new_media.save()
        self.stdout.write('Successfully imported {0} media files'.format(count))

    def connect_media_with_s3(self):
        """
        Goes through the media files and old artist/event join tables and connects the correct
        media file for each artist/event with the files already uploaded to S3.
        """
        for event_join in Joinmediaevent.objects.using('old').all():
            try:
                event = Event.objects.get(id=event_join.event_id)
                media = Media.objects.get(id=event_join.media_id)
            except (Event.DoesNotExist, Media.DoesNotExist):
                continue
            event.photo = u"images/{0}".format(media.filename)
            event.save()

        for artist_join in Joinmediaperson.objects.using('old').all():
            try:
                artist = Artist.objects.get(id=artist_join.person_id)
                media = Media.objects.get(id=artist_join.media_id)
            except (Artist.DoesNotExist, Media.DoesNotExist):
                continue
            artist.photo = u"images/{0}".format(media.filename)
            artist.save()

    def connect_artist_to_events(self):
        # Artist - Event connection
        leaders = {}
        count = 0
        for old_gig in Joinpersonevent.objects.using('old').all():
            # If the artist type is leader, save the id to assign the leader status later
            if old_gig.persontype_id == 69:
                leaders.setdefault(old_gig.event_id, []).append(old_gig.person_id)
            else:
                try:
                    event = Event.objects.get(id=old_gig.event_id)
                    artist = Artist.objects.get(id=old_gig.person_id)
                except (Artist.DoesNotExist, Event.DoesNotExist):
                    continue
                gig, created = GigPlayed.objects.get_or_create(
                    artist=artist,
                    event=event,
                    role_id=old_gig.persontype_id,
                    sort_order=old_gig.sortorder or ""
                )
                if created:
                    count += 1

        # Assign leader status
        for event_id, artists in leaders.iteritems():
            for artist_id in artists:
                # In some rare cases, artist is only listed as leader, without an instrument
                # so we create a new GigPlayed object with that role
                try:
                    gig = GigPlayed.objects.get(event_id=event_id, artist_id=artist_id)
                    gig.is_leader = True
                    gig.save()
                except GigPlayed.DoesNotExist:
                    gig = GigPlayed.objects.create(
                        artist_id=artist_id,
                        event_id=event_id,
                        role_id=69,
                        is_leader=True,
                        sort_order=-1
                    )

        self.stdout.write('Successfully connected {0} events to artists'.format(count))

    def handle_noargs(self, *args, **options):
        self.migrate_artists()
        self.migrate_events()
        self.connect_artist_to_events()
        self.migrate_media()
        self.connect_media_with_s3()
