from django import forms
from filer.models.filemodels import File, Folder
from oscar.forms.widgets import ImageInput


class PressFileForm(forms.ModelForm):
    class Meta:
        fields = ('name', 'file')
        model = File

    def __init__(self, *args, **kwargs):
        super(PressFileForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['file'].required = True

    def save(self, commit=True):
        object = super(PressFileForm, self).save(commit=False)
        folder, created = Folder.objects.get_or_create(name="Press files")
        object.folder = folder
        object.save()
        return object


class PressPhotoForm(forms.ModelForm):
    class Meta:
        fields = ('name', 'file')
        model = File

    def __init__(self, *args, **kwargs):
        super(PressPhotoForm, self).__init__(*args, **kwargs)
        self.fields['file'].required = True

    def save(self, commit=True):
        object = super(PressPhotoForm, self).save(commit=False)
        folder, created = Folder.objects.get_or_create(name="Press photos")
        object.folder = folder
        object.save()
        return object