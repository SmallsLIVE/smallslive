from allauth.account.views import SignupView as AllauthSignupView
from .forms import UserSignupForm


class SignupView(AllauthSignupView):
    form_class = UserSignupForm


signup_view = SignupView.as_view()