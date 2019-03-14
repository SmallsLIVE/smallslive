from oscar.apps.customer.views import AccountRegistrationView as CoreAccountRegistrationView
from django.shortcuts import get_object_or_404, redirect
from allauth.account.app_settings import EmailVerificationMethod
from allauth.account.utils import complete_signup


class AccountRegistrationView(CoreAccountRegistrationView):
    def form_valid(self, form):
        user = form.save(self.request)
        verification_method = EmailVerificationMethod.OPTIONAL
        complete_signup(self.request, user, verification_method,
                        form.cleaned_data['redirect_url'])
        return redirect(form.cleaned_data['redirect_url'])

    pass
