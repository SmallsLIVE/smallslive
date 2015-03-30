from django import forms
from django.contrib.auth import get_user_model
from django_countries import countries
import floppyforms
from localflavor.us.forms import USStateField
from localflavor.us.us_states import STATE_CHOICES
from events import forms as event_forms
from events.forms import Formset
from events.models import Event

User = get_user_model()

STATE_CHOICES_WITH_EMPTY = ((None, ''),) + STATE_CHOICES
COUNTRIES_WITH_EMPTY = ((None, ''),) + tuple(countries)


class ToggleRecordingStateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('state',)


class EventEditForm(event_forms.EventEditForm):
    class Meta(event_forms.EventEditForm.Meta):
        pass

    def __init__(self, *args, **kwargs):
        super(EventEditForm, self).__init__(*args, **kwargs)
        del self.fields['state']
        del self.fields['start']
        del self.fields['end']
        self.helper[3] = Formset('artists', template='form_widgets/formset_layout.html', admin=False)


class ArtistInfoForm(forms.ModelForm):
    state = USStateField(widget=floppyforms.Select(choices=STATE_CHOICES_WITH_EMPTY))
    country = floppyforms.ChoiceField(choices=COUNTRIES_WITH_EMPTY)
    payout_method = forms.ChoiceField(
        choices=User.PAYOUT_CHOICES,
        widget=forms.RadioSelect()
    )
    paypal_email_again = floppyforms.EmailField(required=False)

    class Meta:
        fields = ('first_name', 'last_name', 'address_1', 'address_2', 'city', 'zip', 'state', 'country',
                  'payout_method', 'paypal_email', 'paypal_email_again')
        model = User

    def __init__(self, *args, **kwargs):
        super(ArtistInfoForm, self).__init__(*args, **kwargs)
        for field in self.Meta.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['state'].widget.attrs['class'] = 'form-control selectpicker'
        self.fields['country'].widget.attrs['class'] = 'form-control selectpicker'
        print self.fields['payout_method'].choices

    def clean(self):
        cleaned_data = super(ArtistInfoForm, self).clean()
        print "a"
        if cleaned_data.get('payout_method') == User.PAYOUT_CHOICES.PayPal:
            msg = u"This field is required."
            if not cleaned_data.get('paypal_email'):
                self.add_error('paypal_email', msg)
            if not cleaned_data.get('paypal_email_again'):
                self.add_error('paypal_email_again', msg)
            if cleaned_data.get('paypal_email') != cleaned_data.get('paypal_email_again'):
                raise forms.ValidationError(u'The two email addresses must match.')
        return cleaned_data
