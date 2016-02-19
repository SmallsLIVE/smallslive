import collections
import logging
from decimal import Decimal
import xlsxwriter
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from artists.models import Artist, ArtistEarnings, CurrentPayoutPeriod, PastPayoutPeriod
from metrics.models import UserVideoMetric
from events.models import Event

logger = logging.getLogger(__name__)

def metrics_data_for_date_period(start_date, end_date):
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

    for artist_id, artist in artists.items():
        artist['ratio'] = Decimal(artist['seconds_played'] / float(total_adjusted_seconds)) if total_adjusted_seconds else 0
    return {
        'metrics_info': artists,
        'total_adjusted_seconds': total_adjusted_seconds,
        'total_event_seconds': total_event_seconds
    }


def update_current_period_metrics():
    current_period = CurrentPayoutPeriod.objects.first()
    metrics = metrics_data_for_date_period(current_period.period_start, current_period.period_end)
    for artist_id, info in metrics['metrics_info'].iteritems():
        Artist.objects.filter(id=artist_id).update(
            current_period_seconds_played=info['seconds_played'],
            current_period_ratio=info['ratio']
        )
    current_period.current_total_seconds = metrics['total_adjusted_seconds']
    current_period.save()
    return True


def generate_payout_sheet(file, start_date, end_date, revenue, operating_expenses, save_earnings=False):
    pool = Decimal((revenue - operating_expenses) / Decimal(2.0))
    metrics = metrics_data_for_date_period(start_date, end_date)
    workbook = xlsxwriter.Workbook(file, {'in_memory': True})
    bold = workbook.add_format({'bold': True})
    sheet = workbook.add_worksheet('Payments')
    sheet.set_column(8, 8, 30)
    sheet.write_row('I1', ('Total event seconds', metrics['total_event_seconds']), bold)
    sheet.write_row('I2', ('Total adjusted seconds', metrics['total_adjusted_seconds']), bold)
    sheet.write_row('I3', ('Revenue', revenue), bold)
    sheet.write_row('I4', ('Operating costs', operating_expenses), bold)
    sheet.write_row('I5', ('Artist money pool', pool), bold)
    headers = ('Artist ID', 'Last name', 'First name', 'Seconds watched', 'Ratio', 'Payment')
    sheet.write_row('A1', headers, bold)

    if save_earnings:
        payout_period = PastPayoutPeriod.objects.create(
            period_start=start_date,
            period_end=end_date,
            total_seconds=metrics['total_adjusted_seconds'],
            total_amount=pool
        )
        Artist.objects.all().update(
            current_period_seconds_played=0,
            current_period_ratio=0
        )
        current_period = CurrentPayoutPeriod.objects.first()
        current_period.period_start = current_period.period_end + relativedelta(days=1)
        current_period.period_end = current_period.period_start + relativedelta(month=3)
        current_period.current_total_seconds = 0
        current_period.save()

    for idx, artist in enumerate(metrics['metrics_info'].items(), start=1):
        ratio = artist[1]['ratio']
        payment = Decimal(ratio * pool)
        sheet.write(idx, 0, artist[0])
        sheet.write(idx, 1, artist[1]['last_name'])
        sheet.write(idx, 2, artist[1]['first_name'])
        sheet.write(idx, 3, artist[1]['seconds_played'])
        sheet.write(idx, 4, ratio)
        sheet.write(idx, 5, payment)
        if save_earnings:
            previous_payout = ArtistEarnings.objects.filter(artist_id=artist[0]).first()
            # balance from previous payout periods carry over only if they exist and they're less than $20
            ledger_balance = 0
            if previous_payout and previous_payout.ledger_balance < 20:
                ledger_balance = previous_payout.ledger_balance

            new_ledger_balance = ledger_balance + payment

            earnings = ArtistEarnings.objects.get_or_create(
                payout_period=payout_period,
                artist_id = artist[0],
                artist_seconds=artist[1]['seconds_played'],
                artist_ratio=ratio,
                amount=payment,
                ledger_balance=new_ledger_balance
            )
    workbook.close()
