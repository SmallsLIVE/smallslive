from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest
from users.models import SmallsEmailAddress
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template.loader import render_to_string
from django.core.mail import send_mail


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