import StringIO
from celery import shared_task
from django.core.mail import EmailMessage
from django.core.files.base import ContentFile

from artist_dashboard.utils import generate_metrics_payout_sheet, \
    generate_donations_payout_sheet, update_current_period_metrics
from artists.models import PastPayoutPeriod


def attach_metrics_payout_sheet(start, end, revenue, operating_expenses, save_earnings):
    output = StringIO.StringIO()
    generate_metrics_payout_sheet(output, start, end, revenue, operating_expenses, save_earnings)
    output.seek(0)
    filename = "payments-{}_{}_{}-{}_{}_{}.xlsx".format(
        start.year, start.month, start.day, end.year, end.month, end.day)
    return output, filename


def attach_donations_payout_sheet(start, end, revenue, operating_expenses, save_earnings):
    output = StringIO.StringIO()
    generate_donations_payout_sheet(output, start, end, revenue, operating_expenses, save_earnings)
    output.seek(0)
    filename = "donations-{}_{}_{}-{}_{}_{}.xlsx".format(
        start.year, start.month, start.day, end.year, end.month, end.day)
    return output, filename


@shared_task(default_retry_delay=10, rate_limit="4/m", max_retries=2)
def generate_payout_sheet_task(start, end, revenue, operating_expenses, save_earnings=False):

    email = EmailMessage(
            "Payment spreadsheet",
            "Spreadsheet for the period {}/{}/{} - {}/{}/{} is attached.".format(
                    start.year, start.month, start.day, end.year, end.month, end.day),
            "aslan1st@mac.com",
            ["aslan1st@mac.com", "martin.prunell@gmail.com"]
    )
    output, filename = attach_metrics_payout_sheet(
        start, end, revenue, operating_expenses, save_earnings)

    email.attach(filename, output.read(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    email.send()

    print '------------------>'
    print 'Sending Email ------>'
    print filename
    if save_earnings:
        period = PastPayoutPeriod.objects.first()
        output.seek(0)
        period.payout_spreadsheet.save(filename, ContentFile(output.read()), save=True)


@shared_task
def update_current_period_metrics_task():
    update_current_period_metrics()
