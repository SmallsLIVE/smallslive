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

from artists.models import Artist, Instrument
from events.models import Event, EventType, GigPlayed
from multimedia.models import MediaType, Media


class Command(BaseCommand):
    args = '<user_data.csv>'
    help = 'Imports user data from the csv file'

    def handle(self, *args, **options):
        if args[0]:
            events = json.load(open(args[0], 'r'))
        else:
            raise CommandError('Provide the path to csv file as an argument to this command')

        for event in events:
            try:
                e = Event.objects.get(id=event.get('eventId'))
            except Event.DoesNotExist:
                e = Event(id=event.get('eventId'))
                e.title = u"{0} {1}".format(event.get('title', ''), event.get('subTitle', ''))
                e.description = event.get('description', '')

                start = arrow.get(event.get('startDay')).naive
                start = timezone.make_aware(start, timezone.get_default_timezone())
                end = arrow.get(event.get('endDay')).naive
                end = timezone.make_aware(end, timezone.get_default_timezone())
                time_string = event.get('dateFreeForm', '\n').lower().splitlines()
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
                e.save()
