import StringIO
from celery import shared_task
from django.core.mail import EmailMessage

from artist_dashboard.utils import generate_payout_sheet, update_current_period_metrics


@shared_task(default_retry_delay=10, rate_limit="4/m", max_retries=2)
def generate_payout_sheet_task(start, end, revenue, operating_expenses, save_earnings=False):
    output = StringIO.StringIO()
    generate_payout_sheet(output, start, end, revenue, operating_expenses, save_earnings)
    output.seek(0)
    filename = "payments-{0}_{1}-{2}_{3}.xlsx".format(start.month, start.year, end.month, end.year)
    email = EmailMessage(
            "Payment spreadsheet",
            "Spreadsheet for the period {}/{} - {}/{} is attached.".format(
                    start.month, start.year, end.month, end.year),
            "smallslive@gmail.com",
            ["smallsjazzclub@gmail.com", "spikewilner@gmail.com"]
    )
    email.attach(filename, output.read(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    email.send()

@shared_task
def update_current_period_metrics_task():
    update_current_period_metrics()
