from oscar.apps.customer.views import AccountRegistrationView as CoreAccountRegistrationView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from allauth.account.app_settings import EmailVerificationMethod
from users.utils import complete_signup


class AccountRegistrationView(CoreAccountRegistrationView):
    def form_valid(self, form):
        user = form.save(self.request)
        verification_method = EmailVerificationMethod.OPTIONAL
        complete_signup(self.request, user, verification_method,
                        form.cleaned_data['redirect_url'])
        return redirect(form.cleaned_data['redirect_url'])

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response
