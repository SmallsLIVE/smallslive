from django import forms
from .models import MediaFile


class TrackFileForm(forms.ModelForm):
    category = forms.ChoiceField(choices=MediaFile.CATEGORY, required=False)

    class Meta:
        model = MediaFile
        fields = ('file',)  # Removed category field for upgrade

    def __init__(self, *args, **kwargs):
        self.category = kwargs.pop('category')
        super(TrackFileForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        file = super(TrackFileForm, self).save(commit=False)
        file.media_type = 'audio'
        file.category = self.category
        file.save()
        return file
