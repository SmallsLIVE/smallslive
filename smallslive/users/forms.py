from allauth.account.models import EmailAddress
from django.conf import settings
import floppyforms as forms
from allauth.account.forms import SignupForm, AddEmailForm


class UserSignupForm(SignupForm):
    email = forms.EmailField(max_length=80, required=True,
                             label="E-mail",
                             widget=forms.EmailInput(attrs={
                                 'placeholder': 'Your e-mail address',
                                 'class': 'form-control'
                             }))
    first_name = forms.CharField(max_length=50, required=False,
                                 label="First name",
                                 widget=forms.TextInput(attrs={
                                     'placeholder': 'Your first name',
                                     'class': 'form-control'
                                 }))
    last_name = forms.CharField(max_length=50, required=False,
                                label="Last name",
                                widget=forms.TextInput(attrs={
                                    'placeholder': 'Your last name',
                                    'class': 'form-control'
                                }))
    terms_of_service = forms.BooleanField(required=False)
    newsletter = forms.BooleanField(required=False)

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        if self.cleaned_data.get('newsletter'):
            user.subscribe_to_newsletter(request)


class EditProfileForm(forms.Form):
    first_name = forms.CharField(max_length=50, required=False,
                                 label="First name",
                                 widget=forms.TextInput(attrs={
                                     'placeholder': 'Your first name',
                                     'class': 'form-control'
                                 }))
    last_name = forms.CharField(max_length=50, required=False,
                                label="Last name",
                                widget=forms.TextInput(attrs={
                                    'placeholder': 'Your last name',
                                    'class': 'form-control'
                                }))
    newsletter = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].initial = self.user.first_name
        self.fields['last_name'].initial = self.user.last_name
        self.fields['newsletter'].initial = self.user.newsletter

    def save(self, request=None):
        self.user.first_name = self.cleaned_data['first_name']
        self.user.last_name = self.cleaned_data['last_name']
        self.user.save()
        if self.cleaned_data.get('newsletter'):
            self.user.subscribe_to_newsletter(request)
        else:
            self.user.unsubscribe_from_newsletter(request)


class ChangeEmailForm(AddEmailForm):
    email = forms.EmailField(max_length=80, required=True,
                             label="E-mail",
                             widget=forms.EmailInput(attrs={
                                 'placeholder': 'Your e-mail address',
                                 'class': 'form-control'
                             }))

    def __init__(self, *args, **kwargs):
        super(ChangeEmailForm, self).__init__(*args, **kwargs)
        self.fields['email'].initial = self.user.email

    def save(self, request):
        old_email = EmailAddress.objects.get(email=self.user.email)
        old_email.change(request, new_email=self.cleaned_data['email'], confirm=True)


class PlanForm(forms.Form):
    def __init__(self, *args, **kwargs):
        selected_plan_type = kwargs.pop('selected_plan_type')
        super(PlanForm, self).__init__(*args, **kwargs)
        if selected_plan_type == 'basic' or selected_plan_type == 'supporter':
            monthly_plan = settings.SUBSCRIPTION_PLANS[selected_plan_type]['monthly']
            plans = [(monthly_plan.get('stripe_plan_id'), monthly_plan)]
        else:
            yearly_plan = settings.SUBSCRIPTION_PLANS[selected_plan_type]['yearly']
            plans = [(yearly_plan.get('stripe_plan_id'), yearly_plan)]
        self.fields['plan'] = forms.ChoiceField(choices=plans)


class ReactivateSubscriptionForm(forms.Form):
    pass
