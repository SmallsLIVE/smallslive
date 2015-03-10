import floppyforms as forms
from .utils import subscribe_to_newsletter


class NewsletterSubscribeForm(forms.Form):
    email = forms.EmailField(max_length=80, required=True,
                             label="E-mail",
                             widget=forms.EmailInput(attrs={
                                 'placeholder': 'Your e-mail address',
                                 'class': 'newsletters__subscribe__input'
                             }))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(NewsletterSubscribeForm, self).__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email

    def subscribe(self, request=None):
        if self.user:
            self.user.subscribe_to_newsletter(request)
        else:
            subscribe_to_newsletter(self.cleaned_data.get('email'), request)
