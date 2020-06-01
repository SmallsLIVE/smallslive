from django.contrib import messages
from django.core.urlresolvers import reverse


def show_modal(request):
    return {'show_modal': request.GET.get('show_modal')}


def check_account_status(request):
    """Show email confirmation dialog only once after authentication"""

    user = request.user

    if not user.is_authenticated():
        return {
            'current_user': user,
            'check_account_status_url': reverse('check_account_status'),
        }

    session = request.session

    flag = session.get('show_email_confirmation_dialog', True)
    show = not user.has_activated_account and flag
    session['show_email_confirmation_dialog'] = False

    # We don't want so show email confirmation when use is trying to buy a ticket.
    if 'payment-details' in request.path:
        show = False

    return {
        'current_user': user,
        'show_email_confirmation_dialog': False,
        'check_account_status_url': reverse('check_account_status'),
    }


def check_if_event_confirmed_user(request):
    """ Needed for showing email confirmation dialog when
    user tries to view a live event"""

    if request.user.is_anonymous():
        user_activated = False
    else:
        user_activated = request.user.has_activated_account

    try:
        return {'is_event_user_not_confirmed': not user_activated}
    except Exception as e:
        print 'Exception!!!'
        return {'is_event_user_not_confirmed': False}


def clean_messages(request):

    if hasattr(request, 'basket'):
        basket = request.basket
        if basket:
            count = basket.lines.filter(product__categories__name='Gifts').count()
            if not count:
                count = basket.lines.filter(product__parent__categories__name='Gifts').count()

            if count:
                storage = messages.get_messages(request)
                if storage:
                    for _ in storage:
                        pass
                        storage.used = True

                    while len(storage._loaded_messages) > 0:
                        del storage._loaded_messages[0]

    return {}