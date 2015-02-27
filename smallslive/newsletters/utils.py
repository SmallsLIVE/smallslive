from mailchimp import Mailchimp
from django.conf import settings


def subscribe_to_newsletter(email):
    mc = Mailchimp(settings.MAILCHIMP_API_KEY)
    try:
        mc.lists.subscribe(settings.MAILCHIMP_LIST_ID, email={'email': email}, double_optin=False)
    except Exception as e:
        return False
    return True


def unsubscribe_from_newsletter(email):
    mc = Mailchimp(settings.MAILCHIMP_API_KEY)
    try:
        mc.lists.unsubscribe(settings.MAILCHIMP_LIST_ID, email={'email': email})
    except Exception as e:
        return False
    return True
