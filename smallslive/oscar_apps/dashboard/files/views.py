from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views import generic
from django_tables2 import SingleTableMixin
from filer.models.filemodels import File
from .forms import PressFileForm, PressPhotoForm, FileForm
from .tables import FileTable, PhotoTable
from django.template.defaultfilters import pluralize


class FileListView(SingleTableMixin, generic.TemplateView):
    table_class = FileTable
    context_table_name = 'files'
    object_name = "file"
    folder_name = "Files"
    template_name = 'dashboard/files/file_list.html'

    def get_context_data(self, **kwargs):
        ctx = super(FileListView, self).get_context_data(**kwargs)
        ctx['queryset_description'] = self.object_name.capitalize()
        ctx['object_name'] = self.object_name
        ctx['object_add_url'] = self.object_add_url()
        ctx['dropzone'] = True
        return ctx

    def get_table_pagination(self):
        return dict(per_page=20)

    def get_queryset(self):
        """
        Build the queryset for this list
        """
        queryset = File.objects.filter(folder__name=self.folder_name)
        return queryset

    def object_add_url(self):
        # Override this in a subclass and return the url that shows the object add form
        return ""


class FileCreateView(generic.CreateView):
    template_name = 'dashboard/files/file_form.html'
    model = File
    form_class = None
    object_name = "file"

    def get_context_data(self, **kwargs):
        ctx = super(FileCreateView, self).get_context_data(**kwargs)
        ctx['title'] = "Add a new {0}".format(self.object_name)
        return ctx

    def get_success_url(self):
        messages.info(self.request, "{0} uploaded successfully".format(self.object_name.capitalize()))
        return reverse("dashboard:index")


class FileUpdateView(generic.UpdateView):
    template_name = 'dashboard/files/file_form.html'
    model = File
    form_class = None
    object_name = "file"

    def get_context_data(self, **kwargs):
        ctx = super(FileUpdateView, self).get_context_data(**kwargs)
        ctx['title'] = "Update {0} '{1}'".format(self.object_name, self.object.name)
        return ctx

    def get_success_url(self):
        messages.info(self.request, "{0} updated successfully".format(self.object_name.capitalize()))
        return reverse("dashboard:index")


class FileDeleteView(generic.DeleteView):
    template_name = 'dashboard/files/file_delete.html'
    model = File
    form_class = FileForm
    object_name = "file"

    def get_context_data(self, *args, **kwargs):
        ctx = super(FileDeleteView, self).get_context_data(*args, **kwargs)
        ctx['title'] = "Delete {0} '{1}'".format(self.object_name, self.object.name)
        return ctx

    def get_success_url(self):
        messages.info(self.request, "{0} deleted successfully".format(self.object_name.capitalize()))
        return reverse("dashboard:index")


class PressFileListView(FileListView):
    object_name = "press file"
    folder_name = "Press files"

    def object_add_url(self):
        return reverse("dashboard:press-file-create")


class PressFileCreateView(FileCreateView):
    form_class = PressFileForm
    object_name = "press file"

    def get_success_url(self):
        super(PressFileCreateView, self).get_success_url()
        return reverse("dashboard:press-file-list")


class PressFileUpdateView(FileUpdateView):
    form_class = PressFileForm
    object_name = "press file"

    def get_success_url(self):
        super(PressFileUpdateView, self).get_success_url()
        return reverse("dashboard:press-file-list")


class PressFileDeleteView(FileDeleteView):
    form_class = PressFileForm
    object_name = "press file"

    def get_success_url(self):
        super(PressFileDeleteView, self).get_success_url()
        return reverse("dashboard:press-file-list")


class PressPhotoListView(FileListView):
    object_name = "press photo"
    folder_name = "Press photos"

    def object_add_url(self):
        return reverse("dashboard:press-photo-create")


class PressPhotoCreateView(FileCreateView):
    form_class = PressPhotoForm
    object_name = "press photo"

    def get_success_url(self):
        super(PressPhotoCreateView, self).get_success_url()
        return reverse("dashboard:press-photo-list")


class PressPhotoUpdateView(FileUpdateView):
    form_class = PressPhotoForm
    object_name = "press photo"

    def get_success_url(self):
        super(PressPhotoUpdateView, self).get_success_url()
        return reverse("dashboard:press-photo-list")


class PressPhotoDeleteView(FileDeleteView):
    form_class = PressPhotoForm
    object_name = "press photo"

    def get_success_url(self):
        super(PressPhotoDeleteView, self).get_success_url()
        return reverse("dashboard:press-photo-list")
