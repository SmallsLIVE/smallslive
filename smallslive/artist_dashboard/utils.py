import collections
import logging
from decimal import Decimal
import xlsxwriter
from artists.models import Artist
from metrics.models import UserVideoMetric
from events.models import Event

logger = logging.getLogger(__name__)


def generate_payout_sheet(start_date, end_date, operating_expenses, revenue):
    pool = Decimal((revenue - operating_expenses) / 2.0)
    events = UserVideoMetric.objects.seconds_played_for_all_events(start_date, end_date)
    artists = collections.OrderedDict()
    for artist in Artist.objects.values('id', 'first_name', 'last_name').order_by('last_name'):
        artists[artist['id']] = {
            'first_name': artist['first_name'],
            'last_name': artist['last_name'],
            'seconds_played': 0
        }
    total_event_seconds = 0
    total_adjusted_seconds = 0
    for event in events:
        try:
            artists_playing = Event.objects.get(id=event.get('event_id')).performers.values_list('id', flat=True)
            total_event_seconds += event.get('seconds_played')
            for artist_id in artists_playing:
                artists[artist_id]['seconds_played'] += event.get('seconds_played')
                total_adjusted_seconds += event.get('seconds_played')
        except Event.DoesNotExist:
            logger.warn('Event {0} does not exist (generating payout)'.format(event.get('event_id')))

    workbook = xlsxwriter.Workbook('payout.xlsx')
    bold = workbook.add_format({'bold': True})
    sheet = workbook.add_worksheet('Payments')
    sheet.set_column(8, 8, 30)
    sheet.write_row('I1', ('Total event seconds', total_event_seconds), bold)
    sheet.write_row('I2', ('Total adjusted seconds', total_adjusted_seconds), bold)
    sheet.write_row('I3', ('Revenue', revenue), bold)
    sheet.write_row('I4', ('Operating costs', operating_expenses), bold)
    sheet.write_row('I5', ('Artist money pool', pool), bold)
    headers = ('Artist ID', 'Last name', 'First name', 'Seconds watched', 'Ratio', 'Payment')
    sheet.write_row('A1', headers, bold)

    for idx, artist in enumerate(artists.items(), start=1):
        ratio = Decimal(artist[1]['seconds_played'] / float(total_adjusted_seconds))
        payment = Decimal(ratio * pool)
        sheet.write(idx, 0, artist[0])
        sheet.write(idx, 1, artist[1]['last_name'])
        sheet.write(idx, 2, artist[1]['first_name'])
        sheet.write(idx, 3, artist[1]['seconds_played'])
        sheet.write(idx, 4, ratio)
        sheet.write(idx, 5, payment)
    workbook.close()
