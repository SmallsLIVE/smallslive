from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views import generic
from django_tables2 import SingleTableMixin
from filer.models.filemodels import File
from .forms import PressFileForm
from .tables import PressFileTable


class PressFileCreateView(generic.CreateView):
    template_name = 'dashboard/files/file_form.html'
    model = File
    form_class = PressFileForm

    def get_context_data(self, **kwargs):
        ctx = super(PressFileCreateView, self).get_context_data(**kwargs)
        ctx['title'] = "Add a new press file"
        return ctx

    def get_success_url(self):
        messages.info(self.request, "Product type created successfully")
        return reverse("dashboard:press-file-list")


class PressFileUpdateView(generic.UpdateView):
    template_name = 'dashboard/files/file_form.html'
    model = File
    form_class = PressFileForm

    def get_context_data(self, **kwargs):
        ctx = super(PressFileUpdateView, self).get_context_data(**kwargs)
        ctx['title'] = "Update product type '%s'" % self.object.name
        return ctx

    def get_success_url(self):
        messages.info(self.request, _("Product type update successfully"))
        return reverse("dashboard:press-file-list")


class PressFileListView(SingleTableMixin, generic.TemplateView):
    """
    Dashboard view of the product list.
    Supports the permission-based dashboard.
    """

    template_name = 'dashboard/files/press_file_list.html'
    table_class = PressFileTable
    context_table_name = 'products'

    def get_context_data(self, **kwargs):
        ctx = super(PressFileListView, self).get_context_data(**kwargs)
        ctx['queryset_description'] = "Press files"
        return ctx

    def get_table_pagination(self):
        return dict(per_page=20)

    def get_queryset(self):
        """
        Build the queryset for this list
        """
        queryset = File.objects.filter(folder__name="Press files")
        return queryset
