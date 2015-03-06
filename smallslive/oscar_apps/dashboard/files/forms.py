from django import forms
from filer.models.filemodels import File, Folder
from oscar.forms.widgets import ImageInput


class PressFileForm(forms.ModelForm):
    class Meta:
        fields = ('name', 'file')
        model = File

    def save(self, commit=True):
        object = super(PressFileForm, self).save(commit=False)
        folder, created = Folder.objects.get_or_create(name="Press files")
        object.folder = folder
        object.save()
        return object
