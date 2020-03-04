import collections
import logging
from decimal import Decimal
import xlsxwriter
from dateutil.relativedelta import relativedelta
from artists.models import Artist, ArtistEarnings, CurrentPayoutPeriod, PastPayoutPeriod
from events.models import Event
from metrics.models import UserVideoMetric
from oscar_apps.catalogue.models import ArtistProduct
from subscriptions.models import Donation

logger = logging.getLogger(__name__)


def metrics_data_for_date_period(start_date, end_date):
    events = UserVideoMetric.objects.seconds_played_for_all_events(start_date, end_date)
    artists = collections.OrderedDict()
    for artist in Artist.objects.values('id', 'first_name', 'last_name').order_by('last_name'):
        artists[artist['id']] = {
            'first_name': artist['first_name'],
            'last_name': artist['last_name'],
            'seconds_played': 0,
            'donations': 0
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
        'total_event_seconds': total_event_seconds,
    }


def donations_data_for_date_period(start_date, end_date, metrics):

    print 'Processing donations ...'

    total_donations = 0

    # Donations to artists
    # Total amount to artist -> take 0%
    donations_sqs = Donation.objects.filter(date__gte=start_date, date__lt=end_date,
                                            confirmed=True, artist_id__isnull=False, amount__gt=0)
    for donation in donations_sqs:
        amount = donation.deductable_amount
        total_donations += donation.amount
        metrics['metrics_info'][donation.artist_id]['donations'] += amount

    # Donations to events
    # Total amount to event -> take 0% -> divide by performers

    donations_sqs = Donation.objects.filter(date__gte=start_date, date__lt=end_date,
                                            confirmed=True, event_id__isnull=False, amount__gt=0)
    for donation in donations_sqs:
        total_donations += donation.amount
        event = Event.objects.filter(pk=donation.event_id).first()
        if event:
            gigs = event.artists_gig_info.all()
            gigs_count = gigs.count()
            if gigs_count:
                amount = donation.deductable_amount / gigs_count
                for gig in gigs:
                    metrics['metrics_info'][gig.artist_id]['donations'] += amount

    # Donations to projects
    # Total amount to project -> take 50% -> divide by leaders
    donations_sqs = Donation.objects.filter(date__gte=start_date, date__lt=end_date,
                                            confirmed=True, product_id__isnull=False, amount__gt=0)
    for donation in donations_sqs:
        total_donations += donation.amount
        products_donations = ArtistProduct.objects.filter(
            product_id=donation.product_id, is_leader=True)
        products_donations_count = products_donations.count()
        if products_donations_count:
            amount = donation.deductable_amount / 2 / products_donations_count
            for product_donation in products_donations:
                metrics['metrics_info'][product_donation.artist_id]['donations'] += amount
        else:
            print 'Warning: no leaders for product {}'.format(donation.product.title)

    metrics['total_donations'] = total_donations

    return metrics


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


def generate_metrics_payout_sheet(file, start_date, end_date,
                                  foundation_total, foundation_costs,
                                  revenue, operating_expenses, save_earnings=False):

    pool = (foundation_total - foundation_costs) / Decimal(2.0)
    # Add extra revenue minus extra cost
    pool += Decimal((revenue - operating_expenses) / Decimal(2.0))
    metrics = metrics_data_for_date_period(start_date, end_date)
    # TODO: under discussion: should donations be on the same spreadsheet?
    metrics = donations_data_for_date_period(start_date, end_date, metrics)
    workbook = xlsxwriter.Workbook(file, {'in_memory': True})
    bold = workbook.add_format({'bold': True})
    sheet = workbook.add_worksheet('Payments')
    sheet.set_column(8, 8, 30)
    sheet.write_row('I1', ('Total event seconds', metrics['total_event_seconds']), bold)
    sheet.write_row('I2', ('Total adjusted seconds', metrics['total_adjusted_seconds']), bold)
    sheet.write_row('I3', ('Deductible Donations to Foundation', foundation_total - foundation_costs), bold)
    sheet.write_row('I4', ('Revenue', revenue), bold)
    sheet.write_row('I5', ('Operating costs', operating_expenses), bold)
    sheet.write_row('I6', ('Artist money pool', pool), bold)
    sheet.write_row('I7', ('Total personal donations', metrics['total_donations']), bold)
    headers = ('Artist ID', 'Last name', 'First name', 'Seconds watched', 'Ratio', 'Payment', 'Personal Donations')
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
        personal_donations = artist[1]['donations']
        sheet.write(idx, 0, artist[0])
        sheet.write(idx, 1, artist[1]['last_name'])
        sheet.write(idx, 2, artist[1]['first_name'])
        sheet.write(idx, 3, artist[1]['seconds_played'])
        sheet.write(idx, 4, ratio)
        sheet.write(idx, 5, payment)
        sheet.write(idx, 6, personal_donations)
        if save_earnings:
            previous_payout = ArtistEarnings.objects.filter(artist_id=artist[0]).first()
            # balance from previous payout periods carry over only if they exist and they're less than $20
            if previous_payout:
                payment += previous_payout.ledger_balance

            if payment > 20:
                new_ledger_balance = 0
            else:
                new_ledger_balance = payment

            earnings = ArtistEarnings.objects.get_or_create(
                payout_period=payout_period,
                artist_id=artist[0],
                artist_seconds=artist[1]['seconds_played'],
                artist_ratio=ratio,
                amount=payment,
                ledger_balance=new_ledger_balance
            )
    workbook.close()


def generate_donations_payout_sheet(file, start_date, end_date, revenue, operating_expenses, save_earnings=False):
    """ Potentially generate donations in another spreadsheet. Under discussion currently."""
    donations = donations_data_for_date_period(start_date, end_date)
    workbook = xlsxwriter.Workbook(file, {'in_memory': True})
    bold = workbook.add_format({'bold': True})
    sheet = workbook.add_worksheet('Donations')
    sheet.set_column(8, 8, 30)
    sheet.write_row('I1', ('Total donations', revenue), bold)
    sheet.write_row('I2', ('Operating costs', operating_expenses), bold)
    headers = ('Artist ID', 'Last name', 'First name', 'Payment')
    sheet.write_row('A1', headers, bold)

    for idx, artist in enumerate(donations['donation_info'].items(), start=1):
        sheet.write(idx, 0, artist[0])
        sheet.write(idx, 1, artist[1]['last_name'])
        sheet.write(idx, 2, artist[1]['first_name'])
        sheet.write(idx, 3, artist[1]['donations'])

    workbook.close()
