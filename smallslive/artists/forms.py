from crispy_forms.layout import Layout, Div, Field
from django import forms
from django.db.models import Count
from django.forms.util import ErrorList
import floppyforms
from crispy_forms.helper import FormHelper
from model_utils import Choices
from haystack.forms import SearchForm

from utils.widgets import ImageCropWidget
from .models import Artist


class ArtistAddForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ('salutation', 'first_name', 'last_name',  'instruments',
                  'biography', 'website', 'photo', 'cropping', 'public_email')
        widgets = {
            'instruments': floppyforms.SelectMultiple,
            'photo': ImageCropWidget,
        }

    def save(self, commit=True):
        artist = super(ArtistAddForm, self).save(commit)
        if commit:
            instruments = self.cleaned_data['instruments']
            for instrument in instruments:
                instrument.artist_count = instrument.artist_count + 1
                instrument.save()

        return artist

    def __init__(self, *args, **kwargs):
        super(ArtistAddForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = 'artist_add'
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.fields['photo'].label = "Upload / Change Profile Photo"


class ArtistInviteForm(forms.Form):
    INVITE_TYPE = Choices(('standard_invite', 'Standard invitation'),
                          ('custom_invite', 'Custom invitation text'),
                          ('no_invite', 'Do not invite right now'))

    email = forms.EmailField(required=False)
    invite_type = forms.ChoiceField(choices=INVITE_TYPE,
                                    widget=forms.RadioSelect,
                                    initial=INVITE_TYPE.standard_invite)
    invite_text = forms.CharField(required=False, widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(ArtistInviteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = 'artist_add'
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'email',
            Div(
                Field('invite_type', template='form_widgets/invite_type_select.html'),
                css_class='alert alert-warning'
            )
        )
        self.fields['invite_text'].label = None

    def clean(self):
        """
        Check that email is entered if sending an invite and check that the custom invite
        text is entered if that option is selected.
        """
        cleaned_data = super(ArtistInviteForm, self).clean()
        invite_type = cleaned_data.get('invite_type')
        email = cleaned_data.get('email')
        invite_text = cleaned_data.get('invite_text')
        if invite_type != self.INVITE_TYPE.no_invite and not email:
            self._errors['email'] = ErrorList(['You have to enter the email address to send an invite'])
        if invite_type == self.INVITE_TYPE.custom_invite and not invite_text:
            self._errors['invite_text'] = ErrorList(['You have to enter custom invite text'])
        return cleaned_data


class ArtistSearchForm(SearchForm):
    instrument = forms.IntegerField(required=False)

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        sqs = super(ArtistSearchForm, self).search()

        if self.cleaned_data.get('q'):
            sqs = self.searchqueryset.filter(content__exact=self.cleaned_data.get('q'))
        elif self.cleaned_data.get('instrument'):
            sqs = self.searchqueryset.filter(instruments=self.cleaned_data.get('instrument'))
        else:
            sqs = self.no_query_found()

        sqs = sqs.load_all_queryset(
            Artist,
            Artist.objects.annotate(events_count=Count('gigs_played')).prefetch_related('instruments')
        )
        return sqs

    def no_query_found(self):
        return self.searchqueryset.all()
