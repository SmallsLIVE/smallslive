import os
from django.core.management import BaseCommand, CommandError
import bleach
import re
import arrow
import json
from bs4 import BeautifulSoup
from django.core.management.base import NoArgsCommand
from django.utils import timezone
from django.utils.dateparse import parse_time
import datetime
import requests

from artists.models import Artist, Instrument
from events.models import Event, EventType, GigPlayed
from multimedia.models import MediaType, Media


class Command(BaseCommand):
    args = '<events.json> <artists.json> <instruments.json>'
    help = 'Imports event data from scraped JSON files'

    def handle(self, *args, **options):
        if len(args) == 3:
            events = json.load(open(args[0], 'r'))
            artists = json.load(open(args[1], 'r'))
            instruments = json.load(open(args[2], 'r'))
        else:
            raise CommandError('Provide the path to csv file as an argument to this command')

        #self.import_instruments(instruments)
        #self.import_artists(artists)
        #self.import_events(events)
        #self.save_images(events)
        self.save_images(artists)

    def import_events(self, events):
        for event in events:
            try:
                e = Event.objects.get(id=event.get('eventId'))
            except Event.DoesNotExist:
                e = self.create_event(event)

    def create_event(self, event_dict):
        e = Event(id=event_dict.get('eventId'))
        e.title = u"{0} {1}".format(event_dict.get('title', '').strip(), event_dict.get('subTitle', '').strip())
        e.description = event_dict.get('description', '')

        start = arrow.get(event_dict.get('startDay')).naive
        start = timezone.make_aware(start, timezone.get_default_timezone())
        end = arrow.get(event_dict.get('endDay')).naive
        end = timezone.make_aware(end, timezone.get_default_timezone())
        time_string = event_dict.get('dateFreeForm', '\n').lower().splitlines()
        if time_string:
            time_string = time_string[0]
            time = time_string.replace('midnight', '12:00').replace(
                'close', '4:00').replace('closing', '4:00').replace(';', ':')
            time = re.sub('[^0-9:]', ' ', time)
            time = time.split()
            if time:
                start_time = time[0]
                if ":" not in start_time:
                    start_time += ":00"
                start_time = parse_time(start_time)
                start = start.replace(hour=start_time.hour, minute=start_time.minute)
                if start_time.hour < 4:
                    start += timezone.timedelta(days=1)
                else:
                    start += timezone.timedelta(hours=12)

                if any(separator in time_string for separator in ['to', 'and', '&']) and len(time) > 1:
                    print time_string
                    print time
                    print e.id
                    end_time = time[1]
                    if ':' not in end_time:
                        end_time += ":00"
                    end_time = parse_time(end_time)
                    end = end.replace(hour=end_time.hour, minute=end_time.minute)
                    if end_time.hour < 6:
                        end += timezone.timedelta(days=1)
                    else:
                        end += timezone.timedelta(hours=12)

                    if 'and' in time_string or '&' in time_string:
                        end += timezone.timedelta(hours=1, minutes=30)
                else:
                    end = start + timezone.timedelta(hours=1, minutes=30)

        e.start = start
        e.end = end

        if event_dict.get('media'):
            e.photo = u"images/{0}".format(event_dict.get('media')[0]['fileName'])

        e.save()

        leaders = {}
        for performer in event_dict.get('performers'):
            if performer.get('personTypeId') == 69:
                leaders.setdefault(e.id, []).append(performer.get('personId'))
            else:
                gig, _ = GigPlayed.objects.get_or_create(
                    artist_id=performer.get('personId'),
                    event_id=e.id,
                    role_id=performer.get('personTypeId'),
                    sort_order=performer.get('sortOrder') or ""
                )

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

        return e

    def import_instruments(self, instruments):
        for ins in instruments:
            instrument, _ = Instrument.objects.get_or_create(id=ins.get('personTypeId'),
                                                             name=ins.get('personType', '').strip())
        return True

    def import_artists(self, artists):
        for art in artists:
            try:
                artist = Artist.objects.get(id=art.get('personId'))
            except Artist.DoesNotExist:
                artist = Artist(id=art.get('personId'))
                artist.biography = self._clean_up_html(art.get('biography', ''))
                artist.first_name = art.get('firstName', '').strip()
                artist.last_name = art.get('lastName', '').strip()
                artist.salutation = art.get('salutation', '').strip()
                website = art.get('website', '')
                artist.website = website.strip() if website else ""
                if art.get('media'):
                    artist.photo = u"images/{0}".format(art.get('media')[0]['fileName'])
                artist.save()

                instrument = Instrument.objects.get(id=art.get('personTypeId'))
                artist.instruments.add(instrument)

    def _clean_up_html(self, text):
        allowed_tags = ['a', 'p']

        # remove all tags except allowed tags
        cleaned_up_html = bleach.clean(text, tags=allowed_tags, strip=True)

        # convert newlines to paragraph tags
        cleaned_up_html = cleaned_up_html.replace("\r\n", "</p><p>")
        cleaned_up_html = cleaned_up_html.replace("\n", "</p><p>")

        # remove empty paragraph tags
        soup = BeautifulSoup(cleaned_up_html, 'html.parser')
        for p in soup.find_all('p'):
            if not p.text.strip():
                p.decompose()

        return unicode(soup)

    def save_images(self, objects):
        if not os.path.exists('images/'):
            os.makedirs('images/')
        images = [e.get('media') for e in objects if e.get('media')]
        count = 0
        for image in images:
            path = image[0]['path'].strip()
            if path[-1] != '/':
                path += '/'
            filename = image[0]['fileName'].strip()
            url = u"{0}{1}".format(path, filename)
            if not os.path.exists(os.path.join(u'images', filename)):
                r = requests.get(url)
                with open(os.path.join(u'images', filename), 'w') as f:
                    f.write(r.content)

            count += 1
            if count % 50 == 0:
                print count
