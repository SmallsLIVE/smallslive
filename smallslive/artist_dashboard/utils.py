import boto
import collections
import logging
from decimal import Decimal
import xlsxwriter
from dateutil.relativedelta import relativedelta
from django.conf import settings
from artists.models import Artist, ArtistEarnings, CurrentPayoutPeriod, \
    PastPayoutPeriod, PayoutPeriodGeneration
from events.models import Event
from metrics.models import UserVideoMetric
from oscar_apps.catalogue.models import ArtistProduct
from subscriptions.models import Donation
from users.models import SmallsUser

logger = logging.getLogger(__name__)


def metrics_data_for_date_period(start_date, end_date):
    events = UserVideoMetric.objects.seconds_played_for_all_events(start_date, end_date)
    artists = collections.OrderedDict()
    for artist in Artist.objects.values('id', 'first_name', 'last_name', 'user').order_by('last_name'):
        user_id = artist['user']
        user = None
        if user_id:
            user = SmallsUser.objects.filter(pk=user_id).first()
        artists[artist['id']] = {
            'first_name': artist['first_name'],
            'last_name': artist['last_name'],
            'seconds_played': 0,
            'donations': 0,
            'user': user,
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


    total_donations = 0
    donation_data=[]

    # Donations to artists
    # Total amount to artist -> take 0%
    donations_sqs = Donation.objects.filter(date__gte=start_date, date__lt=end_date,
                                            confirmed=True, artist_id__isnull=False, amount__gt=0)
    for donation in donations_sqs:
        amount = donation.deductable_amount
        total_donations += donation.deductable_amount
        metrics['metrics_info'][donation.artist_id]['donations'] += amount
        order_number = donation.order.number if donation.order else ''
        item = {
            'user': donation.user.email,
            'date': donation.date,
            'amount': donation.amount,
            'deductible_amount': donation.deductable_amount,
            'artist': donation.artist.full_name(),
            'payment_source': donation.payment_source,
            'reference': donation.reference,
            'order_number': order_number,
        }
        donation_data.append(item)

    # Donations to events
    # Total amount to event -> take 0% -> divide by performers
    donations_sqs = Donation.objects.filter(date__gte=start_date, date__lt=end_date,
                                            confirmed=True, event_id__isnull=False, amount__gt=0)
    for donation in donations_sqs:
        total_donations += donation.deductable_amount
        event = Event.objects.filter(pk=donation.event_id).first()
        if event:
            order_number = donation.order.number if donation.order else ''
            gigs = event.artists_gig_info.all()
            gigs_count = gigs.count()
            if gigs_count:
                amount = donation.deductable_amount / gigs_count
                for gig in gigs:
                    metrics['metrics_info'][gig.artist_id]['donations'] += amount
            item = {
                'user': donation.user.email,
                'date': donation.date,
                'amount': donation.amount,
                'deductible_amount': donation.deductable_amount,
                'event': donation.event.get_absolute_url(),
                'payment_source': donation.payment_source,
                'reference': donation.reference,
                'order_number': order_number,
            }
            donation_data.append(item)

    # Donations to projects
    # Total amount to project -> take 50% -> divide by leaders
    donations_sqs = Donation.objects.filter(date__gte=start_date, date__lt=end_date,
                                            confirmed=True, product_id__isnull=False, amount__gt=0)
    for donation in donations_sqs:
        total_donations += donation.deductable_amount
        products_donations = ArtistProduct.objects.filter(
            product_id=donation.product_id, is_leader=True)
        products_donations_count = products_donations.count()
        if products_donations_count:
            amount = donation.deductable_amount / 2 / products_donations_count
            for product_donation in products_donations:
                metrics['metrics_info'][product_donation.artist_id]['donations'] += amount
        else:
            print('Warning: no leaders for product {}'.format(donation.product.title))
        order_number = donation.order.number if donation.order else ''
        item = {
            'user': donation.user.email,
            'date': donation.date,
            'amount': donation.amount,
            'deductible_amount': donation.deductable_amount,
            'product': donation.product.get_title(),
            'payment_source': donation.payment_source,
            'reference': donation.reference,
            'order_number': order_number
        }
        donation_data.append(item)

    metrics['total_donations'] = total_donations
    metrics['donations'] = donation_data

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


def generate_metrics_payout_sheet(metrics, file, start_date, end_date,
                                  revenue, operating_expenses, save_earnings=False,
                                  process_personal_donations=False):

    # Add extra revenue minus extra cost
    pool = Decimal(revenue - operating_expenses)
    workbook = xlsxwriter.Workbook(file, {'in_memory': True})
    bold = workbook.add_format({'bold': True})
    sheet = workbook.add_worksheet('Payments')
    sheet.set_column(8, 8, 30)
    sheet.write_row('L1', ('Total event seconds', metrics['total_event_seconds']), bold)
    sheet.write_row('L2', ('Total adjusted seconds', metrics['total_adjusted_seconds']), bold)
    sheet.write_row('L4', ('Revenue', revenue), bold)
    sheet.write_row('L5', ('Operating costs', operating_expenses), bold)

    if process_personal_donations:
        sheet.write_row('L7', ('Total personal donations', metrics['total_donations']), bold)
        headers = ('Artist ID', 'Last name', 'First name', 'Seconds watched', 'Ratio', 'Payment', 'Personal Donations', 'Address', 'PayPal ID', 'Tax Payer ID')
    else:
        headers = ('Artist ID', 'Last name', 'First name', 'Seconds watched', 'Ratio', 'Payment')
    sheet.write_row('A1', headers, bold)

    if save_earnings and process_personal_donations:
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
        if process_personal_donations:
            personal_donations = artist[1]['donations']
            sheet.write(idx, 6, personal_donations)
            user = artist[1]['user']
            if user:
                sheet.write(idx, 7, user.get_formatted_address())
                sheet.write(idx, 8, user.paypal_email or '')
                sheet.write(idx, 9, user.taxpayer_id or '')
        if save_earnings and process_personal_donations:
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


def generate_donations_payout_sheet(donations, file):
    """ Potentially generate donations in another spreadsheet. Under discussion currently."""
    workbook = xlsxwriter.Workbook(file, {'in_memory': True})
    bold = workbook.add_format({'bold': True})
    sheet = workbook.add_worksheet('Donations')
    headers = ('User', 'Date', 'Amount', 'Deductible', 'Artist', 'Event',
               'Product', 'Payment Source', 'Reference', 'Order Number')
    sheet.write_row('A1', headers, bold)

    for idx, item in enumerate(donations, start=1):
        sheet.write(idx, 0, item['user'])
        sheet.write(idx, 1, item['date'].strftime('%m/%d/%Y'))
        sheet.write(idx, 2, item['amount'])
        sheet.write(idx, 3, item['deductible_amount'])
        sheet.write(idx, 4, item.get('artist', ''))
        sheet.write(idx, 5, item.get('event', ''))
        sheet.write(idx, 6, item.get('product', ''))
        sheet.write(idx, 7, item.get('payment_source', ''))
        sheet.write(idx, 8, item.get('reference', ''))
        sheet.write(idx, 9, item.get('order_number', ''))

    workbook.close()


def get_metrics_payout_file_name(start, end, personal=False):
    if personal:
        filename = "payments-admin-{}_{}_{}-{}_{}_{}.xlsx".format(
            start.year, start.month, start.day, end.year, end.month, end.day)
    else:
        filename = "payments-musicians-{}_{}_{}-{}_{}_{}.xlsx".format(
            start.year, start.month, start.day, end.year, end.month, end.day)

    return filename


def start_generate_payout_sheet(start, end):

    data = {
        'period_start': start,
        'period_end': end,
    }
    payout = PayoutPeriodGeneration.objects.get_or_create(**data)[0]
    payout.status = PayoutPeriodGeneration.STATUSES.processing
    payout.save()


def end_generate_payout_sheet(start, end):

    payout_generation = PayoutPeriodGeneration.objects.filter(
        period_start=start, period_end=end).first()
    payout_generation.status = PayoutPeriodGeneration.STATUSES.success
    payout_generation.save()


def get_payout_bucket():
    conn = boto.connect_s3(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                           aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                           calling_format=boto.s3.connection.OrdinaryCallingFormat())

    try:
        bucket_name = 'payout-sheets'
        bucket = conn.create_bucket(bucket_name, location=boto.s3.connection.Location.DEFAULT)
    except boto.exception.S3CreateError as e:
        if 'BucketAlreadyExists' in str(e):
            bucket = conn.get_bucket(bucket_name)

    return bucket
