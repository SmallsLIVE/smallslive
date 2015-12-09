import smtplib

import djrill
from celery import shared_task

from users.models import SmallsUser


@shared_task(bind=True, default_retry_delay=10, rate_limit="120/m", max_retries=3)
def send_email_confirmation(request, user_id, signup=True, activate_view='account_confirm_email'):
    user = SmallsUser.objects.get(id=user_id)
    try:
        send_email_confirmation(request, user, signup=signup, activate_view=activate_view)
    except (djrill.MandrillAPIError, smtplib.SMTPException) as e:
        raise self.retry(exc=e)
