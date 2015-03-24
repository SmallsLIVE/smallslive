from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Div
import floppyforms as forms
from allauth.account.forms import SetPasswordForm, BaseSignupForm
from users.utils import send_email_confirmation


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
            StrictButton('Complete registration', css_class="btn-primary", type="submit"),
        )
        self.fields['email'].read_only = True
        self.fields['email'].help_text = "This is used to log in to SmallsLIVE. You can update it now if you want to."
    
    def save(self):
        self.user.email = self.cleaned_data['email']
        super(SetUserDataForm, self).save()


class InviteArtistForm(BaseSignupForm):

    def __init__(self, *args, **kwargs):
        self.artist = kwargs.pop('artist')
        super(InviteArtistForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_tag = False

    def invite_artist(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        user = adapter.save_user(request, user, self)
        self.artist.user = user
        self.artist.save()
        self.custom_signup(request, user)
        # TODO: Move into adapter `save_user` ?
        setup_user_email(request, user, [])
        send_email_confirmation(request, user, activate_view='artist_registration_confirm_email')
        return user
