from allauth.account.models import EmailAddress
import floppyforms as forms
from allauth.account.forms import SignupForm, AddEmailForm


class UserSignupForm(SignupForm):
    email = forms.EmailField(max_length=80, required=True,
                             label="E-mail",
                             widget=forms.TextInput(attrs={
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
    terms_of_service = forms.BooleanField(required=True)
    newsletter = forms.BooleanField()

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        if self.cleaned_data.get('newsletter'):
            user.subscribe_to_newsletter()


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

    def save(self):
        self.user.first_name = self.cleaned_data['first_name']
        self.user.last_name = self.cleaned_data['last_name']
        self.user.save()
        if self.cleaned_data.get('newsletter'):
            self.user.subscribe_to_newsletter()
        else:
            self.user.unsubscribe_from_newsletter()


class ChangeEmailForm(AddEmailForm):
    email = forms.EmailField(max_length=80, required=True,
                             label="E-mail",
                             widget=forms.TextInput(attrs={
                                 'placeholder': 'Your e-mail address',
                                 'class': 'form-control'
                             }))

    def __init__(self, *args, **kwargs):
        super(ChangeEmailForm, self).__init__(*args, **kwargs)
        self.fields['email'].initial = self.user.email

    def save(self, request):
        old_email = EmailAddress.objects.get(email=self.user.email)
        old_email.change(request, new_email=self.cleaned_data['email'], confirm=True)
