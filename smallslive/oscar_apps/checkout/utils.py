from oscar.apps.checkout.utils import CheckoutSessionData as CoreCheckoutSessionData


class CheckoutSessionData(CoreCheckoutSessionData):
    def set_reservation_name(self, first_name, last_name):
        self._set('guest', 'first_name', first_name)
        self._set('guest', 'last_name', last_name)

    def get_reservation_name(self):
        first_name = self._get('guest', 'first_name')
        last_name = self._get('guest', 'last_name')
        return (first_name, last_name)
