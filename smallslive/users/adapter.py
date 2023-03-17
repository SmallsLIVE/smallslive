from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.urls import reverse
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string

from email_validator import validate_email, EmailNotValidError
import floppyforms as forms


class SmallsLiveAdapter(DefaultAccountAdapter):

    def add_message(self, *args, **kwargs):
        """Avoid messages"""
        pass

    def clean_email(self, email):
        try:
            v = validate_email(email)
            email = v["email"]
        except EmailNotValidError as e:
            raise forms.ValidationError("The email address is invalid. Perhaps there was a typo? Please try again.")

        return email

    def get_email_confirmation_redirect_url(self, request):
        redirect_url = super(SmallsLiveAdapter, self).get_email_confirmation_redirect_url(request)

        # Confirmation was sent from donate
        if request.GET.get('donate') == 'True':
            redirect_url = reverse('email_confirmed_donate')

        # Confirmation was sent from support on catalog
        if request.GET.get('catalog') == 'True':
            next = request.GET.get('next', '')
            if next:
                next = '?next=' + next
            redirect_url = reverse('email_confirmed_catalog') + next

        return redirect_url

    def render_mail(self, template_prefix, email, context):
        """
        Renders an e-mail to `email`.  `template_prefix` identifies the
        e-mail that is to be sent, e.g. "account/email/email_confirmation"
        """
        subject = render_to_string('{0}_subject.txt'.format(template_prefix),
                                   context)
        # remove superfluous line breaks
        subject = " ".join(subject.splitlines()).strip()
        subject = self.format_email_subject(subject)

        bodies = {}
        for ext in ['html', 'txt']:
            try:
                template_name = '{0}_message.{1}'.format(template_prefix, ext)
                bodies[ext] = render_to_string(template_name,
                                               context).strip()
            except TemplateDoesNotExist:
                if ext == 'txt' and not bodies:
                    # We need at least one body
                    raise
        if 'txt' in bodies:
            msg = EmailMultiAlternatives(subject,
                                         bodies['txt'],
                                         settings.DEFAULT_FROM_REGISTRATION_EMAIL,
                                         [email])
            if 'html' in bodies:
                msg.attach_alternative(bodies['html'], 'text/html')
        else:
            msg = EmailMessage(subject,
                               bodies['html'],
                               settings.DEFAULT_FROM_REGISTRATION_EMAIL,
                               [email])
            msg.content_subtype = 'html'  # Main content is now text/html
        return msg
