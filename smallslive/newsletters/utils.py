import sys
import traceback
from mailchimp import Mailchimp
from django.contrib import messages
from django.conf import settings


def subscribe_to_newsletter(email, request=None):
    mc = Mailchimp(settings.MAILCHIMP_API_KEY)
    subscribed = True
    try:
        mc.lists.subscribe(settings.MAILCHIMP_LIST_ID, email={'email': email}, double_optin=False)
    except Exception as e:
        subscribed = False
    if request:
        if subscribed:
            messages.success(request, "You've been subscribed to the SmallsLIVE newsletter.")
        else:
            print >> sys.stderr, traceback.format_exc()
            messages.error(request, "There's been an error while trying to subscribe to the SmallsLIVE newsletter.")
    return subscribed


def unsubscribe_from_newsletter(email, request=None):
    mc = Mailchimp(settings.MAILCHIMP_API_KEY)
    unsubscribed = True
    try:
        mc.lists.unsubscribe(settings.MAILCHIMP_LIST_ID, email={'email': email})
    except Exception as e:
        unsubscribed = False
    if request:
        if unsubscribed:
            messages.success(request, "You've been unsubscribed from the SmallsLIVE newsletter.")
        else:
            messages.error(request, "There's been an error while trying to unsubscribe from the SmallsLIVE newsletter.")
    return unsubscribed
