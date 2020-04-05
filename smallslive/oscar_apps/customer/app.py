from django.conf.urls import url, include
from oscar.apps.customer.app import CustomerApplication as CoreCustomerApplication
from .views import AccountRegistrationView


class CustomerApplication(CoreCustomerApplication):
    def get_urls(self):
        urls = super(CustomerApplication, self).get_urls()
        urls += [
            url(r'^store_register/$',
                AccountRegistrationView.as_view(),
                name='register_view'),
        ]
        return self.post_process_urls(urls)


application = CustomerApplication()
