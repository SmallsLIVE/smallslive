from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.urls import reverse
from django.template.loader import render_to_string


def send_admin_donation_notification(donation):

    admin_list = settings.ADMIN_EMAILS

    if not admin_list:
        return

    ctx = {
        'donation': donation,
    }
    if donation.order:
        protocol = getattr(settings, 'DEFAULT_HTTP_PROTOCOL', 'http')
        site = Site.objects.get_current()
        uri = reverse('dashboard:order-detail', kwargs={'number': donation.order.number})
        ctx['order_url'] = '{}://{}{}'.format(protocol, site, uri)
    subject = render_to_string('subscriptions/email/subject.txt', ctx)
    message = render_to_string('subscriptions/email/body.txt', ctx)
    subject = subject.strip()
    EmailMessage(
        subject,
        message,
        to=admin_list,
        from_email='admin@smallslive.com').send()
