import sys

from django.contrib import messages
from django.urls import reverse
from django.views import generic
from django.views.generic import View
from django_tables2 import SingleTableMixin
from filer.models.filemodels import File
from .forms import FileForm
from .tables import FileTable, PhotoTable


class FileHandlingMixin(object):
    def get_context_data(self, **kwargs):
        ctx = super(FileHandlingMixin, self).get_context_data(**kwargs)
        ctx['queryset_description'] = self.object_name.capitalize()
        ctx['category'] = self.kwargs.get("category")
        ctx['object_name'] = self.object_name
        ctx['full_object_name'] = self.full_object_name
        return ctx

    @property
    def folder_name(self):
        return "{0}s".format(self.full_object_name.capitalize())

    @property
    def full_object_name(self):
        return self.kwargs.get("category", "").replace("-", " ").replace("_", " ")

    @property
    def object_name(self):
        return self.kwargs.get("category", "").replace("-", " ").replace("_", " ").split(" ")[1]


class FileListView(FileHandlingMixin, SingleTableMixin, generic.TemplateView):
    context_table_name = 'files'
    template_name = 'dashboard/files/file_list.html'

    def get_table_class(self):
        if "photo" in self.kwargs.get('category'):
            return PhotoTable
        else:
            return FileTable

    def get_context_data(self, **kwargs):
        ctx = super(FileListView, self).get_context_data(**kwargs)
        ctx['object_add_url'] = reverse("dashboard:file-create", kwargs={"category": self.kwargs.get("category")})
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

file_list = FileListView.as_view()


class FileCreateView(FileHandlingMixin, generic.CreateView):
    template_name = 'dashboard/files/file_form.html'
    model = File
    form_class = FileForm

    def get_form_kwargs(self):
        kwargs = super(FileCreateView, self).get_form_kwargs()
        kwargs['folder_name'] = self.folder_name
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(FileCreateView, self).get_context_data(**kwargs)
        ctx['title'] = "Add a new {0}".format(self.object_name)
        return ctx

    def get_success_url(self):
        messages.info(self.request, "{0} uploaded successfully".format(self.object_name.capitalize()))
        return reverse("dashboard:file-list", kwargs={"category": self.kwargs.get("category")})

file_create = FileCreateView.as_view()


class FileUpdateView(FileHandlingMixin, generic.UpdateView):
    template_name = 'dashboard/files/file_form.html'
    model = File

    def get_context_data(self, **kwargs):
        ctx = super(FileUpdateView, self).get_context_data(**kwargs)
        ctx['title'] = "Update {0} '{1}'".format(self.object_name, self.object.name)
        return ctx

    def get_success_url(self):
        messages.info(self.request, "{0} updated successfully".format(self.object_name.capitalize()))
        return reverse("dashboard:file-list", kwargs={"category": self.kwargs.get("category")})

file_edit = FileUpdateView.as_view()


class FileDeleteView(FileHandlingMixin, generic.DeleteView):
    template_name = 'dashboard/files/file_delete.html'
    model = File

    def get_context_data(self, *args, **kwargs):
        ctx = super(FileDeleteView, self).get_context_data(*args, **kwargs)
        ctx['title'] = "Delete {0} '{1}'".format(self.object_name, self.object.name)
        return ctx

    def get_success_url(self):
        messages.info(self.request, "{0} deleted successfully".format(self.object_name.capitalize()))
        return reverse("dashboard:file-list", kwargs={"category": self.kwargs.get("category")})

file_delete = FileDeleteView.as_view()
