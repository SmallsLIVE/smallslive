from django.conf.urls import url, include
from oscar.apps.checkout.app import CheckoutApplication as CoreCheckoutApplication
from oscar.core.loading import get_class
from oscar_apps.checkout.views import ExecutePayPalPaymentView


class CheckoutApplication(CoreCheckoutApplication):
    files_app = get_class('dashboard.files.app', 'application')

    def get_urls(self):
        urls = super(CheckoutApplication, self).get_urls()
        urls += [
            url(r'^files/', include(self.files_app.urls)),
            url(r'^paypal/execute/$', ExecutePayPalPaymentView.as_view(),
                name='paypal_execute'),
        ]
        return self.post_process_urls(urls)


application = CheckoutApplication()
