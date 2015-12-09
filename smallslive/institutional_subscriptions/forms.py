from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from multi_email_field.forms import MultiEmailField
from allauth.account.utils import user_username, user_email
from institutional_subscriptions.tasks import send_email_confirmation
from .models import Institution

User = get_user_model()


class InstitutionAddForm(forms.ModelForm):
    subscription_start = forms.DateTimeField(label="Start time", required=True, input_formats=['%m/%d/%Y %I:%M %p'])
    subscription_end = forms.DateTimeField(label="End time", required=True, input_formats=['%m/%d/%Y %I:%M %p'])

    class Meta:
        model = Institution
        fields = ('name', 'subscription_start', 'subscription_end')

    def __init__(self, *args, **kwargs):
        super(InstitutionAddForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = 'institution_add'
        self.helper.form_method = 'post'
        self.helper.form_tag = False


class InstitutionMembersInviteForm(forms.Form):
    member_emails = MultiEmailField(required=True)

    def __init__(self, institution=None, *args, **kwargs):
        super(InstitutionMembersInviteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = 'institution_invite_members'
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.institution = institution

    def clean(self):
        if not self.institution.is_subscription_active():
            raise ValidationError("The subscription is not active and you can't invite members")
        return self.cleaned_data

    def invite_members(self, request):
        adapter = get_adapter()
        members = []
        for email in self.cleaned_data.get('member_emails'):
            print email
            try:
                user = User.objects.get(email=email)
                if not user.institution:
                    user.institution = self.institution
                    user.save()
                    members.append(user)
            except ObjectDoesNotExist:
                user = adapter.new_user(request)
                user.email = email
                user.institution = self.institution
                user.set_unusable_password()
                adapter.populate_username(request, user)
                user.save()
                setup_user_email(request, user, [])
                members.append(user)
            send_email_confirmation.delay(request, user, signup=True, activate_view='account_confirm_email')
            storage = messages.get_messages(request)
            storage.used = True
            messages.success(request, 'Members successfully invited')
        return members

    def raise_duplicate_email_error(self):
        # don't raise errors, used for resending invites to users
        pass
