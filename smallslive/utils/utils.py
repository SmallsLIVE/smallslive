import logging

from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest
from users.models import SmallsEmailAddress
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template.loader import render_to_string
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def resend_email_confirmation_to_user(user):
    req = HttpRequest()
    req.session = {}
    req.META['SERVER_NAME'] = 'www.smallslive.com'
    req.META['SERVER_PORT'] = '443'
    req.META['HTTP_X_FORWARDED_PROTO'] = 'https'
    print("Sending {0}".format(user.email))
    email = SmallsEmailAddress.objects.get(user=user, email=user.email)
    if user.artist:
        email.send_confirmation(req, signup=True, activate_view="artist_registration_confirm_email")
    else:
        email.send_confirmation(req, signup=True, activate_view="account_confirm_email")


def clean_messages(request):
    """
    Cleans django messages.
    :param request:
    :return:
    """
    storage = messages.get_messages(request)
    for _ in storage:
        pass
    storage.used = True


def send_order_confirmation_email(email, message=None):
    code = 'ORDER_PLACED'
    email_content = {
        'html': True,
        'subject': 'order placed',
        'body': 'this is your order'
    }
    from_email = settings.OSCAR_FROM_EMAIL
    to_email = email
    html_message = render_to_string('emails/order-confirmation-email.html', message)
    if email_content['html']:
        send_mail(email_content['subject'],
                  email_content['body'],
                  from_email,
                  [to_email],
                  html_message=html_message)


def send_order_refunded_email(email, message=None):
    email_content = {
        'html': True,
        'subject': 'Order Refunded',
        'body': 'this is your order'
    }
    from_email = settings.OSCAR_FROM_EMAIL
    to_email = email
    html_message = render_to_string('emails/order-refund-email.html', message)
    if email_content['html']:
        send_mail(email_content['subject'],
                  email_content['body'],
                  from_email,
                  [to_email],
                  html_message=html_message)


def send_event_update_email(updated_by, event, base_url):
    if not updated_by.artist:
        return

    email_content = {
        'subject': 'Event Updated',
        'body': 'Event has been updated',
    }

    update_details = {
        'artist_name': updated_by.get_full_name(),
        'event_id': event.id,
        'event_title': event.title,
        'event_full_title': event.full_title(),
        'event_url': event.get_absolute_url(),
        'event_slug': event.slug,
        'event_date': event.date,
        'base_url': base_url,
    }

    from_email = settings.OSCAR_FROM_EMAIL
    to_email = settings.EVENT_UPDATE_RECEIVER

    try:
        html_message = render_to_string('emails/event-update-email.html', update_details)
        print("-------------- Sending Event update email ----------------")
        print(f"--------- Sender {from_email}-------------")
        print(f"------- Receiver {to_email} -------------")

        send_mail(email_content['subject'],
                  email_content['body'],
                  from_email,
                  to_email,
                  html_message=html_message)
        logger.info(f"Event update email has been sent for {event.id}")
    except Exception as E:
        logger.error(f"Event update email failed for event {event.id}. Reason {str(E)}", exc_info=True)