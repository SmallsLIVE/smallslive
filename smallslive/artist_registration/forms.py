from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Div
from django import forms
from allauth.account.forms import SetPasswordForm


class SetUserDataForm(SetPasswordForm):
    email = forms.EmailField()

    def __init__(self, user=None, *args, **kwargs):
        super(SetUserDataForm, self).__init__(user, *args, **kwargs)
        self.fields['email'].initial = self.user.email
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'email',
            'password1',
            'password2',
            StrictButton('Continue Artist Registration', css_class="btn-primary", type="submit"),
            HTML('<p class="set-password-contact">Contact <a href="#">artistHelp@smallslive.com</a> for help.</p>'),
        )
        self.fields['email'].help_text = "This is used to log in to SmallsLIVE. You can update it now if you want to."
    
    def save(self):
        self.user.email = self.cleaned_data['email']
        super(SetUserDataForm, self).save()
