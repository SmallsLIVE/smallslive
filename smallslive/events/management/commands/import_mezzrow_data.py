from pprint import pprint

from django.core.management import BaseCommand, CommandError
import json

from artists.models import Artist, Instrument
from events.models import Event, EventType, GigPlayed, Venue


class Command(BaseCommand):
    args = '<alldata.json>'
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
        if len(args) >= 1:
            mezzrow_data = json.load(open(args[0], 'r'))
        else:
            raise CommandError(
                'Provide the path to json file as an argument to this command'
            )

        # Create Mezzrow venue if it does not exist
        self.mezzrow_venue, _ = Venue.objects.get_or_create(
            name='Mezzrow Jazz Club'
        )

        # Delete previous import events
        Event.objects.filter(venue=self.mezzrow_venue).delete()

        # Group data
        grouped_data = {}
        for item in mezzrow_data:
            model = item.get('model')
            grouped_data.setdefault(model, [])
            grouped_data[model].append(item)

        print(
            '{} types of item: {}'.format(
                len(grouped_data), grouped_data.keys()
            )
        )
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
            item = single_import_func(fields)
            self.mappings[mappings_name][old_pk] = item.pk

        return True

    def import_instrument(self, fields):
        name = fields['name']
        print(u'Importing Instrument {}'.format(name))
        intrument, created = Instrument.objects.get_or_create(
            name=name, defaults=fields
        )
        return intrument

    def import_artist(self, fields):
        first_name = fields.pop('first_name').strip()
        last_name = fields.pop('last_name').strip()
        instruments = fields.pop('instruments')
        fields.pop('user')
        print(u'Importing artist {} {}'.format(first_name, last_name))
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
            # TODO Create relation if necesary
            pass

        return artist

    def import_eventtype(self, fields):
        name = fields['name']
        print(u'Importing event type: {}'.format(name))
        eventtype, created = EventType.objects.get_or_create(
            name=name, defaults=fields
        )
        return eventtype

    def import_event(self, fields):
        print(u'Importing event: {}'.format(fields['title']))
        fields.pop('streamable')
        fields.pop('last_modified_by')

        old_event_type = fields['event_type']
        if old_event_type:
            types_map = self.mappings['events.eventtype']
            fields['event_type'] = types_map[old_event_type]

        fields['venue'] = self.mezzrow_venue
        event = Event.objects.create(**fields)
        return event

    def import_gigplayed(self, fields):
        old_artist = fields.pop('artist')
        old_role = fields.pop('role')
        old_event = fields.pop('event')

        fields['artist_id'] = self.mappings['artists.artist'][old_artist]
        fields['role_id'] = self.mappings['artists.instrument'][old_role]
        fields['event_id'] = self.mappings['events.event'][old_event]

        gigplayed = GigPlayed.objects.create(**fields)

        return gigplayed
