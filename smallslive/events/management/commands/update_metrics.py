from django.core.management import BaseCommand, CommandError
from django.db.models import Sum
from events.models import Event, EventSet
from metrics.models import UserVideoMetric


class Command(BaseCommand):
    args = ''
    help = ''

    def handle(self, *args, **options):

        qs = UserVideoMetric.objects.values('event_id')
        qs = qs.annotate(play_count=Sum('play_count'), seconds_played=Sum('seconds_played'))
        count = 0
        for item in qs.order_by('-event_id'):
            count += 1
            print 'Processing:', count, item
            event = Event.objects.filter(pk=item['event_id']).first()
            if event:
                play_count = item['play_count']
                seconds_played = item['seconds_played']
                needs_updating = event.play_count != play_count or event.seconds_played != seconds_played
                if needs_updating:
                    event.play_count = play_count
                    event.seconds_played = seconds_played
                    event.save()
                    print '--> saved!', event.seconds_played
