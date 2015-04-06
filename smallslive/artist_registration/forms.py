from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Div
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
import floppyforms as forms
from allauth.account.forms import SetPasswordForm, BaseSignupForm
from users.utils import send_email_confirmation

User = get_user_model()


class CompleteSignupForm(SetPasswordForm):
    email = forms.EmailField()

    def __init__(self, user=None, *args, **kwargs):
        super(CompleteSignupForm, self).__init__(user, *args, **kwargs)
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
        self.fields['email'].initial = self.user.email
        self.fields['email'].help_text = "This is used to log in to SmallsLIVE. You can update it now if you want to."


class InviteArtistForm(BaseSignupForm):

    def __init__(self, *args, **kwargs):
        self.artist = kwargs.pop('artist')
        super(InviteArtistForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_tag = False

    def invite_artist(self, request):
        adapter = get_adapter()
        try:
            user = User.objects.get(email=self.cleaned_data.get('email'))
        except ObjectDoesNotExist:
            user = adapter.new_user(request)
            user = adapter.save_user(request, user, self)
            user.artist = self.artist
            user.save()
            self.custom_signup(request, user)
            # TODO: Move into adapter `save_user` ?
            setup_user_email(request, user, [])
        send_email_confirmation(request, user, activate_view='artist_registration_confirm_email')
        return user

    def raise_duplicate_email_error(self):
        # don't raise errors, used for resending invites to users
        pass