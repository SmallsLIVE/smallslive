from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import user_pk_to_url_str, user_username
from allauth.utils import build_absolute_uri

from crispy_forms.layout import Layout
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django_countries import countries
import floppyforms
import allauth.account.forms as allauth_forms
from extra_views import InlineFormSet
from localflavor.us.forms import USStateField
from localflavor.us.us_states import STATE_CHOICES
from artists.forms import ArtistAddForm
from artists.models import Artist, CurrentPayoutPeriod
from events import forms as event_forms
from events.forms import Formset
from events.models import Recording, GigPlayed

User = get_user_model()

STATE_CHOICES_WITH_EMPTY = (('', 'State'),) + STATE_CHOICES
COUNTRIES_WITH_EMPTY = (('', 'Country'),) + tuple(countries)


class ToggleRecordingStateForm(forms.ModelForm):
    class Meta:
        model = Recording
        fields = ('state',)


class ArtistGigPlayedAddInlineFormSet(InlineFormSet):
    model = GigPlayed
    fields = ('artist', 'role', 'is_leader', 'sort_order')
    extra = 0
    can_delete = False

    def construct_formset(self):
        formset = super(ArtistGigPlayedAddInlineFormSet, self).construct_formset()
        for num, form in enumerate(formset):
            form.fields['artist'].empty_label = "Artist"
            form.fields['artist'].widget.attrs['class'] = "artist_field"
            form.fields['role'].empty_label = "Role"
            form.fields['role'].widget.attrs['class'] = "role_field"
            form.fields['is_leader'].initial = False
            form.fields['is_leader'].label = 'Leader'
            form.fields['sort_order'].initial = num
            form.fields['sort_order'].widget = forms.HiddenInput()
            form.fields['sort_order'].widget.attrs['class'] = "sort_order_field"
        return formset


class ArtistGigPlayedEditLazyInlineFormSet(ArtistGigPlayedAddInlineFormSet):
    """
    Filter the dropdowns so we can use selectize and autocomplete instead
    of loading the full artist list.
    """

    can_delete = True


class EventEditForm(event_forms.EventEditForm):

    start_streaming_before_minutes = forms.IntegerField(initial=15, widget=forms.HiddenInput)

    class Meta(event_forms.EventEditForm.Meta):
        pass

    def get_layout(self):
        return Layout(
            'title',
            Formset('artists', template='form_widgets/formset_layout.html'),
            'photo',
            'cropping'
        )

    def __init__(self, *args, **kwargs):
        super(EventEditForm, self).__init__(*args, **kwargs)
        del self.fields['venue']
        del self.fields['subtitle']
        del self.fields['state']
        del self.fields['date']


class EventAjaxEditForm(EventEditForm):

    def __init__(self, *args, **kwargs):
        super(EventAjaxEditForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if 'class' in self.fields[field].widget.attrs:
                class_names = self.fields[field].widget.attrs['class'].split(' ')
                if 'form-control' not in class_names:
                    class_names.append('form-control')
                    print class_names
                    self.fields[field].widget.attrs['class'] = ' '.join(class_names)
            else:
                self.fields[field].widget.attrs['class'] = 'form-control'


class ArtistInfoForm(forms.ModelForm):
    state = USStateField(widget=floppyforms.Select(choices=STATE_CHOICES_WITH_EMPTY), required=False)
    country = floppyforms.ChoiceField(choices=COUNTRIES_WITH_EMPTY)
    payout_method = forms.ChoiceField(
        choices=User.PAYOUT_CHOICES,
        widget=forms.RadioSelect()
    )
    paypal_email_again = floppyforms.EmailField(required=False)

    class Meta:
        fields = ('first_name', 'last_name', 'address_1', 'address_2', 'city', 'zip', 'state', 'country',
                  'payout_method', 'paypal_email', 'paypal_email_again', 'taxpayer_id')
        model = User

    def __init__(self, *args, **kwargs):
        super(ArtistInfoForm, self).__init__(*args, **kwargs)
        for field in self.Meta.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['state'].widget.attrs['class'] = 'form-control selectpicker'
        self.fields['country'].widget.attrs['class'] = 'form-control selectpicker'
        # default to US if nothing is set, initial not working as the form is bound
        if not self.initial.get('country'):
            self.initial['country'] = 'US'
        
        self.fields['first_name'].widget.attrs['placeholder'] = self.fields['first_name'].label
        self.fields['last_name'].widget.attrs['placeholder'] = self.fields['last_name'].label
        self.fields['address_1'].widget.attrs['placeholder'] = self.fields['address_1'].label
        self.fields['address_2'].widget.attrs['placeholder'] = self.fields['address_2'].label
        self.fields['city'].widget.attrs['placeholder'] = self.fields['city'].label
        self.fields['zip'].widget.attrs['placeholder'] = self.fields['zip'].label
        self.fields['state'].widget.attrs['placeholder'] = self.fields['state'].label
        self.fields['country'].widget.attrs['placeholder'] = self.fields['country'].label

    def clean(self):
        cleaned_data = super(ArtistInfoForm, self).clean()
        if cleaned_data.get('payout_method') == User.PAYOUT_CHOICES.PayPal:
            msg = u"This field is required."
            if not cleaned_data.get('paypal_email'):
                self.add_error('paypal_email', msg)
            if not cleaned_data.get('paypal_email_again'):
                self.add_error('paypal_email_again', msg)
            if cleaned_data.get('paypal_email') != cleaned_data.get('paypal_email_again'):
                raise forms.ValidationError(u'The two email addresses must match.')

        if cleaned_data.get('country') == 'US':
            state = cleaned_data.get('state')
            if not state:
                self.add_error('state', 'You must select a valid US state or territory.')
            taxpayer_id = cleaned_data.get('taxpayer_id')
            # if not taxpayer_id:
            #     self.add_error('taxpayer_id', 'You must enter a valid taxpayer ID as a US citizen.')
            self.fields['state'].clean(state)
            self.fields['taxpayer_id'].clean(state)
        else:
            cleaned_data['state'] = ''
            cleaned_data['taxpayer_id'] = ''
        return cleaned_data


class EditProfileForm(ArtistAddForm):
    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields['website'].widget = forms.TextInput()
        for field in self.Meta.fields:
            self.fields[field].widget.attrs['class'] = self.fields[field].widget.attrs.get('class', '') + ' form-control'
        self.fields['salutation'].widget.attrs['class'] = 'form-control selectpicker'
        self.fields['website'].widget.attrs['placeholder'] = 'http://www.yourwebsite.com'


class ArtistResetPasswordForm(allauth_forms.ResetPasswordForm):
    def save(self, request, **kwargs):
        # c/p from parent class, only needed to change the URL in the email
        email = self.cleaned_data["email"]
        token_generator = kwargs.get("token_generator",
                                     default_token_generator)

        for user in self.users:

            temp_key = token_generator.make_token(user)

            # save it to the password reset model
            # password_reset = PasswordReset(user=user, temp_key=temp_key)
            # password_reset.save()

            current_site = Site.objects.get_current()

            # send the password reset email
            path = reverse("artist_dashboard:reset_password_from_key",
                           kwargs=dict(uidb36=user_pk_to_url_str(user),
                                       key=temp_key))
            url = build_absolute_uri(request, path,
                                     protocol=app_settings.DEFAULT_HTTP_PROTOCOL)
            context = {"site": current_site,
                       "user": user,
                       "password_reset_url": url}
            if app_settings.AUTHENTICATION_METHOD \
                    != app_settings.AuthenticationMethod.EMAIL:
                context['username'] = user_username(user)
            get_adapter().send_mail('account/email/password_reset_key',
                                    email,
                                    context)
        return self.cleaned_data["email"]


class MetricsPayoutForm(forms.Form):
    period_start = forms.DateField(required=True)
    period_end = forms.DateField(required=True)
    revenue = forms.DecimalField(required=True)
    operating_cost = forms.DecimalField(required=True)
    save_earnings = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(MetricsPayoutForm, self).__init__(*args, **kwargs)
        current_period = CurrentPayoutPeriod.objects.first()
        self.fields['period_start'].initial = current_period.period_start
        self.fields['period_end'].initial = current_period.period_end
