from django.core.management.base import NoArgsCommand
from events.models import Event
from django.utils.timezone import datetime, timedelta


class Command(NoArgsCommand):
    help = 'Push the last 60 events in the DB to the future, starting from the current date, 2 events per day'

    def handle_noargs(self, *args, **options):
        slot = 1
        start_date = datetime.now()
        events = list(Event.objects.all().order_by('-start')[:60])
        events.reverse()
        for e in events:
            e.start = start_date
            if slot == 1:
                e.start = e.start.replace(hour=19, minute=0, second=0, microsecond=0)
                e.end = e.start.replace(hour=21)
                slot += 1
            elif slot == 2:
                e.start = e.start.replace(hour=21, minute=0, second=0, microsecond=0)
                e.end = e.start.replace(hour=23)
                slot = 1
                start_date = start_date + timedelta(days=1)
            e.save()
