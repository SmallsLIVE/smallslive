from django.conf import settings
import floppyforms
import stripe
from django import forms
from localflavor.us import forms as us_forms
from localflavor.us.us_states import STATE_CHOICES
from model_utils import Choices
from oscar.apps.checkout import forms as checkout_forms

STATE_CHOICES_WITH_EMPTY = (('', ''),) + STATE_CHOICES
stripe.api_key = settings.STRIPE_SECRET_KEY


class ShippingAddressForm(checkout_forms.ShippingAddressForm):
    state = us_forms.USStateField(widget=floppyforms.Select(choices=STATE_CHOICES_WITH_EMPTY), required=False)


class PaymentForm(forms.Form):
    PAYMENT_CHOICES = Choices('paypal', 'credit-card')
    payment_method = forms.ChoiceField(required=True, choices=PAYMENT_CHOICES)
    number = forms.CharField(required=True, min_length=16, max_length=20)
    exp_month = forms.CharField(required=True, max_length=2)
    exp_year = forms.CharField(required=True, min_length=2, max_length=4)
    cvc = forms.CharField(required=True, min_length=3, max_length=4)
    name = forms.CharField(required=True)

    def clean(self):
        data = super(PaymentForm, self).clean()
        if not self.errors:
            try:
                token = stripe.Token.create(
                    card={
                        "number": data.get('number'),
                        "exp_month": data.get('exp_month'),
                        "exp_year": data.get('exp_year'),
                        "cvc": data.get('cvc'),
                        "name": data.get('name'),
                    },
                )
                self.token = token.id
            except stripe.error.CardError, e:
                error = e.json_body['error']
                self.add_error(error['param'], error['message'])
        return data
