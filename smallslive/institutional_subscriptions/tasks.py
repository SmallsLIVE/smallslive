import smtplib

import djrill
from celery import shared_task
from django.http import HttpRequest

from users.utils import send_email_confirmation_for_celery

from users.models import SmallsUser


@shared_task(default_retry_delay=10, rate_limit="120/m", max_retries=3)
def send_email_confirmation_task(user_id, signup=True, activate_view='institution_member_confirm_email'):
    print("OVO JE USER {}".format(user_id))
    req = HttpRequest()
    req.session = {}
    req.META['SERVER_NAME'] = 'www.smallslive.com'
    req.META['SERVER_PORT'] = '443'
    req.META['HTTP_X_FORWARDED_PROTO'] = 'https'
    user = SmallsUser.objects.get(id=user_id)
    try:
        send_email_confirmation_for_celery(req, user, signup=signup, activate_view=activate_view)
    except (djrill.MandrillAPIError, smtplib.SMTPException) as e:
        raise self.retry(exc=e)
