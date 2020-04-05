from oscar.apps.payment.exceptions import PaymentError


class RedirectRequiredAjax(PaymentError):
    """
    Exception to be used when payment processsing requires a redirect
    """

    def __init__(self, url, reference):
        self.url = url
        self.reference = reference
