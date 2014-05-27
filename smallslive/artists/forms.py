from crispy_forms.helper import FormHelper
from django.forms import ModelForm, SelectMultiple
from events.forms import ImageThumbnailWidget
from .models import Artist


class ArtistAddForm(ModelForm):
    class Meta:
        model = Artist
        fields = ('salutation', 'first_name', 'last_name',  'instruments', 'biography', 'website', 'photo')
        widgets = {
            'instruments': SelectMultiple,
            'photo': ImageThumbnailWidget
        }

    def __init__(self, *args, **kwargs):
        super(ArtistAddForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = 'artist_add'
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.fields['photo'].label = "Photo (portrait-style JPG w/ instrument preferred)"
