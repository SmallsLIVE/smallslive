from django.conf import settings
from djstripe.models import Customer
import floppyforms
import stripe
from django import forms
from localflavor.us import forms as us_forms
from localflavor.us.us_states import STATE_CHOICES
from model_utils import Choices
from oscar.apps.checkout import forms as checkout_forms
from oscar.apps.payment import forms as payment_forms
from oscar.apps.order.models import BillingAddress
from oscar.apps.address.models import UserAddress

from oscar.apps.checkout.forms import GatewayForm as CoreGatewayForm
from oscar.apps.customer.utils import normalise_email
from email_validator import validate_email, EmailNotValidError


STATE_CHOICES_WITH_EMPTY = (('', ''),) + STATE_CHOICES
stripe.api_key = settings.STRIPE_SECRET_KEY


class ShippingAddressForm(checkout_forms.ShippingAddressForm):
    state = us_forms.USStateField(widget=floppyforms.Select(choices=STATE_CHOICES_WITH_EMPTY), required=False)

    def __init__(self, *args, **kwargs):
        super(ShippingAddressForm, self).__init__(*args, **kwargs)
        self.fields['country'].empty_label = ""


class PaymentForm(forms.Form):
    PAYMENT_CHOICES = Choices('paypal', 'credit-card', 'existing-credit-card')
    payment_method = forms.ChoiceField(required=True, choices=PAYMENT_CHOICES, initial='credit-card')
    card_number = forms.CharField(required=True, min_length=16, max_length=20)
    exp_month = forms.CharField(required=True, max_length=2)
    exp_year = forms.CharField(required=True, min_length=2, max_length=4)
    cvc = forms.CharField(required=True, min_length=3, max_length=4)
    name = forms.CharField(required=True)

    def __init__(self, user, stripe_api_key, *args, **kwargs):
        self.stripe_api_key = stripe_api_key
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.user = user
        if user.is_authenticated():
            try:
                customer = Customer.objects.get(subscriber=user)
                if customer and customer.can_charge():
                    self.fields['payment_method'].choices.insert(1, ('existing-credit-card', 'existing-credit-card'))
                    self.fields['payment_method'].initial = 'existing-credit-card'
                    self.can_use_existing = True
            except Customer.DoesNotExist:
                pass

    def clean(self):
        existing_cc = self.data.get('payment_method', None) == 'existing-credit-card'
        data = super(PaymentForm, self).clean()
        if not self.errors:
            if existing_cc:
                stripe_customer = self.user.customer.stripe_customer
                self.token = stripe_customer.get('default_source')
                try:
                    card_info = stripe_customer.get('sources', {}).get('data', {})[0]
                    data['name'] = card_info.get('name')
                    data['card_number'] = card_info.get('last4')
                except IndexError:
                    pass
            else:
                try:
                    token = stripe.Token.create(
                        api_key=self.stripe_api_key,
                        card={
                            'number': data.get('card_number'),
                            'exp_month': data.get('exp_month'),
                            'exp_year': data.get('exp_year'),
                            'cvc': data.get('cvc'),
                            'name': data.get('name'),
                        },
                    )
                    self.token = token.id
                    print 'Sripe token: ', token
                except stripe.error.CardError, e:
                    print 'ERROR !!!!'
                    print e
                    error = e.json_body['error']
                    print error
                    if error['param'] == 'number':
                        error['param'] = 'card_number'
                    self.add_error(error['param'], error['message'])
        return data

    def _post_clean(self):
        # Don't run model validation if using shipping address
        if self.data.get('payment_method', None) == 'existing-credit-card':
            return
        super(PaymentForm, self)._post_clean()


class BillingAddressForm(payment_forms.BillingAddressForm):
    """
    Extended version of the core billing address form that adds a field so
    customers can choose to re-use their shipping address.
    """
    SAME_AS_SHIPPING, NEW_ADDRESS = 'same-address', 'different-address'
    CHOICES = (
        (SAME_AS_SHIPPING, 'Use shipping address'),
        (NEW_ADDRESS, 'Enter a new address'),
    )
    billing_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=CHOICES, initial=SAME_AS_SHIPPING)
    state = us_forms.USStateField(widget=floppyforms.Select(choices=STATE_CHOICES_WITH_EMPTY), required=False)

    class Meta(payment_forms.BillingAddressForm):
        model = UserAddress
        exclude = ('search_text', 'user', 'num_orders', 'hash', 'is_default_for_billing', 'is_default_for_shipping')

    def __init__(self, shipping_address, user, data=None, *args, **kwargs):
        # Store a reference to the shipping address
        self.shipping_address = shipping_address

        super(BillingAddressForm, self).__init__(data, *args, **kwargs)

        self.instance.user = user

        # If no shipping address (eg a download), then force the
        # 'same_as_shipping' field to have a certain value.
        if shipping_address is None:
            self.fields['billing_option'].choices = (
                (self.NEW_ADDRESS, 'Enter a new address'),)
            self.fields['billing_option'].initial = self.NEW_ADDRESS

        # If using same address as shipping, we don't need require any of the
        # required billing address fields.
        if data and data.get('billing_option', None) == self.SAME_AS_SHIPPING:
            for field in self.fields:
                if field != 'billing_option':
                    self.fields[field].required = False

    def _post_clean(self):
        # Don't run model validation if using shipping address
        if self.cleaned_data.get('billing_option') == self.SAME_AS_SHIPPING:
            return
        super(BillingAddressForm, self)._post_clean()

    def save(self, commit=True):

        if self.cleaned_data.get('billing_option') == self.SAME_AS_SHIPPING:
            # Convert shipping address into billing address
            billing_addr = BillingAddress()
            self.shipping_address.populate_alternative_model(billing_addr)
            if commit:
                billing_addr.save()
            return billing_addr
        else:
            address = super(BillingAddressForm, self).save(commit=False)
            try:
                address = UserAddress.objects.get(
                    user=self.instance.user,
                    hash=address.generate_hash())
                    
                last_address = UserAddress.objects.get(user=self.instance.user, is_default_for_billing=True)
                last_address.is_default_for_billing = False
                
                address.is_default_for_billing = True
                address.save()
                
            except UserAddress.DoesNotExist:
                address.is_default_for_billing = True
                address.save()
            return address

    def validate_unique(self):
        pass


class GatewayForm(CoreGatewayForm):
    username = forms.EmailField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    first_name = forms.CharField(max_length=150, required=False,
                                       widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=150, required=False,
                                       widget=forms.TextInput(attrs={'placeholder': 'Last name'}))
    password = forms.CharField(label=("Password"), widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    
    def clean(self):
        if not self.is_guest_checkout():
            if 'first_name' in self.errors:
                del self.errors['first_name']
            if 'last_name' in self.errors:
                del self.errors['last_name']
        return super(GatewayForm, self).clean()

    def clean_username(self):
        email = normalise_email(self.cleaned_data['username'])
        try:
            v = validate_email(email)
            email = v["email"]
        except EmailNotValidError as e:
            raise forms.ValidationError("The email address is invalid. Perhaps there was a typo? Please try again.")
        return email
