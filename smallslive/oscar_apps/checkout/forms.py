import floppyforms
from localflavor.us import forms as us_forms
from localflavor.us.us_states import STATE_CHOICES
from oscar.apps.checkout import forms as checkout_forms

STATE_CHOICES_WITH_EMPTY = (('', ''),) + STATE_CHOICES


class ShippingAddressForm(checkout_forms.ShippingAddressForm):
    state = us_forms.USStateField(widget=floppyforms.Select(choices=STATE_CHOICES_WITH_EMPTY), required=False)
