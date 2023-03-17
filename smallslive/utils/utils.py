from django.contrib import messages
from django.http import HttpRequest
from users.models import SmallsEmailAddress


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
