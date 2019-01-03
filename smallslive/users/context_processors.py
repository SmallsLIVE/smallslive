

def show_modal(request):
    return {'show_modal': request.GET.get('show_modal')}


def check_account_status(request):
    """Show email confirmation dialog only once after authentication"""

    user = request.user

    if not user.is_authenticated():
        return {}

    session = request.session

    flag = session.get('show_email_confirmation_dialog', True)
    show = not user.has_activated_account and flag
    session['show_email_confirmation_dialog'] = False

    return {'show_email_confirmation_dialog': show}

def check_if_event_confimed_user(request):
    try:
        event = request.is_event and not request.user.has_activated_account
        return {'is_event': event}
    except Exception as e:
        return {'is_event': False}