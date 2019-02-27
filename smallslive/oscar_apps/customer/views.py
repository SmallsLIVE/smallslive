from oscar.apps.customer.views import AccountRegistrationView as CoreAccountRegistrationView


class AccountRegistrationView(CoreAccountRegistrationView):
    def form_valid(self, form):
        print "///"
        print form
        print "///"
        return super(AccountRegistrationView, self).form_valid(form)

    pass
