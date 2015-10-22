import time
from django.core.management.base import NoArgsCommand
from django.http import HttpRequest
from users.models import SmallsUser, SmallsEmailAddress


class Command(NoArgsCommand):
    help = ''

    def handle_noargs(self, *args, **options):
        artists = SmallsUser.objects.exclude(artist=None).filter(emailaddress__verified=False)
        print artists
        req = HttpRequest()
        req.session = {}
        req.META['SERVER_NAME'] = 'www.smallslive.com'
        req.META['SERVER_PORT'] = '443'
        for user in artists:
            print "Sending {0}".format(user.email)
            email = SmallsEmailAddress.objects.get(user=user, email=user.email)
            email.send_confirmation(req, signup=True, activate_view="artist_registration_confirm_email")
            time.sleep(1)
