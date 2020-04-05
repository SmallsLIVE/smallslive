import json
from pprint import pprint

from django.core.management import BaseCommand, CommandError
from django.utils import timezone

from artists.models import Artist, Instrument
from events.models import Event, EventType, GigPlayed, Venue


class Command(BaseCommand):
    args = 'artists.json events.json'
    help = 'Imports event data from scraped JSON files'

    def __init__(self):
        super(Command, self).__init__()

        self.mezzrow_venue = None
        self.mappings = {
            'artists.instrument': {},
            'artists.artist': {},
            'events.eventtype': {},
            'events.event': {},
            'events.gigplayed': {},
        }

    def handle(self, *args, **options):

        with open('smallslive/artists_mezzrow.json') as f:
            mezzrow_artists_data = json.loads(f.read())
        with open('smallslive/events_mezzrow.json') as f:
            mezzrow_events_data = json.loads(f.read())

        # Create Mezzrow venue if it does not exist
        self.mezzrow_venue, _ = Venue.objects.get_or_create(
            name='Mezzrow',
            audio_bucket_name='Mezzrowmp3',
            video_bucket_name='MezzrowVid'
        )

        # Delete previous import events
        Event.objects.filter(venue=self.mezzrow_venue).delete()

        # Group data
        grouped_data = {}
        for item in mezzrow_artists_data:
            model = item.get('model')
            if model not in grouped_data:
                print model
            grouped_data.setdefault(model, [])
            grouped_data[model].append(item)

        for item in grouped_data['artists.artist']:
            print '{}, {}'.format(item['fields']['last_name'].encode('utf-8'), item['fields']['first_name'].encode('utf-8'))

        a_list = Artist.objects.all().order_by('last_name', 'first_name')

        for a in a_list:
            print '{}, {}'.format(
                a.last_name.encode('utf-8'),
                a.first_name.encode('utf-8'))

        for item in mezzrow_events_data:
            model = item.get('model')
            if model not in grouped_data:
                print model
            grouped_data.setdefault(model, [])
            grouped_data[model].append(item)

        self.import_model(
            grouped_data, 'artists.instrument', self.import_instrument
        )
        self.import_model(
            grouped_data, 'artists.artist', self.import_artist
        )
        self.import_events(grouped_data)
        #self.save_images(events)
        # self.save_images(artists)

    def import_events(self, grouped_data):
        self.import_model(grouped_data, 'events.eventtype',
                          self.import_eventtype)

        # Fix eventtype parents
        for old_pk, new_pk in self.mappings['events.eventtype'].iteritems():
            if old_pk != new_pk:
                EventType.objects.filter(parent=old_pk).update(parent=new_pk)

        self.import_model(grouped_data, 'events.event', self.import_event)
        self.import_model(grouped_data, 'events.gigplayed',
                          self.import_gigplayed)

    def import_model(self, grouped_data, mappings_name,
                     single_import_func):
        data_list = grouped_data[mappings_name]
        for item_data in data_list:
            old_pk = item_data['pk']
            fields = item_data['fields']
            item = single_import_func(fields, old_pk=old_pk)
            if item:
                self.mappings[mappings_name][old_pk] = item.pk
            else:
                print 'No data: {}'.format(item_data)

        return True

    def import_instrument(self, fields, old_pk=None):
        name = fields['name']
        print(u'Importing Instrument {}'.format(name))
        instrument, created = Instrument.objects.get_or_create(
            name=name, defaults=fields
        )
        return instrument

    def import_artist(self, fields, old_pk=None):
        first_name = fields.pop('first_name').strip()
        last_name = fields.pop('last_name').strip()
        if not first_name and not last_name:
            return None

        instruments = fields.pop('instruments')
        instruments = [Instrument.objects.get(pk=x) for x in instruments]

        fields.pop('user')
        print('Importing artist {} {}'.format(first_name.encode('utf-8'), last_name.encode('utf-8')))
        try:
            artist = Artist.objects.get(
                first_name=first_name, last_name=last_name
            )
        except Artist.MultipleObjectsReturned:
            artist = Artist.objects.filter(
                first_name=first_name, last_name=last_name
            ).order_by('pk').first()

        except Artist.DoesNotExist:
            artist = Artist.objects.create(
                first_name=first_name, last_name=last_name,
                **fields
            )
        for instrument in instruments:
            if not artist.instruments.filter(pk=instrument.pk).exists():
                artist.instruments.add(instrument)
                instrument.artist_count = instrument.artist_count + 1
                instrument.save()

        return artist

    def import_eventtype(self, fields, old_pk=None):
        name = fields['name']
        print('Importing event type: {}'.format(name.encode('utf-8')))
        eventtype, created = EventType.objects.get_or_create(
            name=name, defaults=fields
        )
        return eventtype

    def import_event(self, fields, old_pk=None):

        print('Importing event: {}'.format(fields['title'].encode('utf-8')))
        fields.pop('streamable')
        fields.pop('last_modified_by')

        old_event_type = fields['event_type']
        if old_event_type:
            types_map = self.mappings['events.eventtype']
            fields['event_type'] = types_map[old_event_type]

        fields['venue'] = self.mezzrow_venue
        if old_pk:
            fields['original_id'] = old_pk
        fields['import_date'] = timezone.now()

        event = Event.objects.create(**fields)

        return event

    def import_gigplayed(self, fields, old_pk=None):
        old_artist = fields.pop('artist')
        old_role = fields.pop('role')
        old_event = fields.pop('event')

        fields['artist_id'] = self.mappings['artists.artist'][old_artist]
        fields['role_id'] = self.mappings['artists.instrument'][old_role]
        fields['event_id'] = self.mappings['events.event'][old_event]

        gigplayed = GigPlayed.objects.create(**fields)

        return gigplayed
