from django import forms
from django.contrib.auth import get_user_model
from oscar.apps.customer.forms import EmailUserCreationForm as CoreEmailUserCreationForm

User = get_user_model()


class EmailUserCreationForm(CoreEmailUserCreationForm):

    first_name = forms.CharField(
        max_length=50,
        required=False,
        label="First name",
        widget=forms.TextInput(attrs={
            'placeholder': 'Your first name',
            'class': 'form-control'
        }))
    last_name = forms.CharField(
        max_length=50,
        required=False,
        label="Last name",
        widget=forms.TextInput(attrs={
            'placeholder': 'Your last name',
            'class': 'form-control'
        }))

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super(EmailUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if 'username' in [f.name for f in User._meta.fields]:
            user.username = generate_username()
        if commit:
            user.save()

        return user