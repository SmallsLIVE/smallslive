from io import BytesIO
from celery import shared_task
from django.core.files.base import ContentFile

from datetime import datetime

from artists.models import PayoutPeriodGeneration
from artist_dashboard.utils import generate_metrics_payout_sheet, \
    generate_donations_payout_sheet, update_current_period_metrics, \
    get_metrics_payout_file_name, end_generate_payout_sheet, \
    metrics_data_for_date_period, donations_data_for_date_period
from artists.models import PastPayoutPeriod


def attach_metrics_payout_sheet(metrics, start, end,
                                revenue, operating_expenses,
                                save_earnings, process_personal_donations=False):

    output = BytesIO()
    generate_metrics_payout_sheet(metrics, output, start, end,
                                  revenue, operating_expenses,
                                  save_earnings, process_personal_donations)
    output.seek(0)
    filename = get_metrics_payout_file_name(start, end, personal=process_personal_donations)
    return output, filename


def attach_donations_sheet(donations, start, end):

    output = BytesIO()
    generate_donations_payout_sheet(donations, output)
    output.seek(0)
    filename = 'donations-admin-{}_{}_{}-{}_{}_{}.xlsx'.format(
            start.year, start.month, start.day, end.year, end.month, end.day)
    return output, filename


@shared_task(default_retry_delay=10, rate_limit="4/m", max_retries=2)
def generate_payout_sheet_task(start, end,
                               revenue, operating_expenses,
                               save_earnings=False):
    """ Deprecate email in favor of download. Generate file and upload to s3.
    Poll to download when ready"""

    # Spreadsheet for admins with personal donations.
    revenue = float(revenue)
    operating_expenses = float(operating_expenses)

    metrics = metrics_data_for_date_period(start, end)
    metrics = donations_data_for_date_period(start, end, metrics)
    output, file_name = attach_metrics_payout_sheet(
        metrics,
        start, end,
        revenue, operating_expenses,
        save_earnings, process_personal_donations=True)
    PayoutPeriodGeneration.objects.attach_admin_spreadsheet(start, end, output, file_name)

    if save_earnings:
        period = PastPayoutPeriod.objects.first()
        output.seek(0)
        period.admin_payout_spreadsheet.save(file_name, ContentFile(output.read()), save=True)

    # Spreadsheet for musicians does not contain personal
    # Donations
    output, file_name = attach_metrics_payout_sheet(
        metrics,
        start, end,
        revenue, operating_expenses,
        save_earnings, process_personal_donations=False)
    PayoutPeriodGeneration.objects.attach_musicians_spreadsheet(start, end, output, file_name)

    if save_earnings:
        period = PastPayoutPeriod.objects.first()
        output.seek(0)
        period.musicians_payout_spreadsheet.save(file_name, ContentFile(output.read()), save=True)

    # Direct donation information
    output, file_name = attach_donations_sheet(metrics['donations'], start, end)
    PayoutPeriodGeneration.objects.attach_donations_spreadsheet(start, end, output, file_name)


    end_generate_payout_sheet(start, end, )


@shared_task
def update_current_period_metrics_task():
    update_current_period_metrics()
