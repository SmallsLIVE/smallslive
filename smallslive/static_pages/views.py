from django.contrib.flatpages.models import FlatPage
from django.views.generic import TemplateView, ListView, DetailView
from filer.models import File, Folder
from events.models import Event, Recording
from .filters import ArchiveFilter, EventsListFilter
from django.utils import timezone
from braces.views import StaffuserRequiredMixin


class AboutUsView(DetailView):
    template_name = "flatpages/about-us.html"
    context_object_name = "page"

    def get_object(self, queryset=None):
        return FlatPage.objects.get(title="About us")

    def get_context_data(self, **kwargs):
        context = super(AboutUsView, self).get_context_data(**kwargs)
        files_folder, _ = Folder.objects.get_or_create(name="About photos")
        context['files'] = files_folder.files
        return context

about_view = AboutUsView.as_view()


class ManageArchiveView(StaffuserRequiredMixin, ListView):
    template_name = 'manage_archive.html'
    context_object_name = "archives"
    filterset_class = ArchiveFilter
    paginate_by = 30

    def get_queryset(self):
        return Event.objects.filter(
            recordings__media_file__isnull=False).distinct()
    
    def get_context_data(self, **kwargs):
        context = super(ManageArchiveView, self).get_context_data(**kwargs)
        context['filter'] = self.filterset_class(self.request.GET, queryset=self.get_queryset())
        paginator = context['paginator']
        page = paginator.page(self.request.GET.get('page', 1))
        adjacent_pages = 2
        startPage = max(page.number - adjacent_pages, 1)
        if startPage <= 3:
            startPage = 1
        endPage = page.number + adjacent_pages + 1
        if endPage >= paginator.num_pages - 1:
            endPage = paginator.num_pages + 1
        page_numbers = [n for n in range(startPage, endPage) if n > 0 and n <= paginator.num_pages]
        context.update({
            'page_numbers': page_numbers,
            'show_first': 1 not in page_numbers,
            'show_last': paginator.num_pages not in page_numbers,
            })
        
        if self.request.GET.get('title'):
            filter = self.filterset_class(self.request.GET, queryset=self.get_queryset())
            context['archives'] = filter.qs
            context.pop('paginator', None)
            context.pop('page_obj', None)

        return context
    
manage_archive = ManageArchiveView.as_view()

class ManageEventsListView(StaffuserRequiredMixin, ListView):
    template_name = 'events_list.html'
    context_object_name = "events"
    filterset_class = EventsListFilter
    paginate_by = 30

    def get_queryset(self):
        return Event.objects.filter(start__gte=timezone.now()).order_by('start')
    
    def get_context_data(self, **kwargs):
        context = super(ManageEventsListView, self).get_context_data(**kwargs)
        context['filter'] = self.filterset_class(self.request.GET, queryset=self.get_queryset())
        paginator = context['paginator']
        page = paginator.page(self.request.GET.get('page', 1))
        adjacent_pages = 2
        startPage = max(page.number - adjacent_pages, 1)
        if startPage <= 3:
            startPage = 1
        endPage = page.number + adjacent_pages + 1
        if endPage >= paginator.num_pages - 1:
            endPage = paginator.num_pages + 1
        page_numbers = [n for n in range(startPage, endPage) if n > 0 and n <= paginator.num_pages]
        context.update({
            'page_numbers': page_numbers,
            'show_first': 1 not in page_numbers,
            'show_last': paginator.num_pages not in page_numbers,
            })
        
        if self.request.GET.get('title'):
            filter = self.filterset_class(self.request.GET, queryset=self.get_queryset())
            context['events'] = filter.qs
            context.pop('paginator', None)
            context.pop('page_obj', None)

        return context
    
manage_events_list = ManageEventsListView.as_view()


class PressView(DetailView):
    template_name = "press.html"
    context_object_name = "page"

    def get_object(self, queryset=None):
        return FlatPage.objects.get(title="Press")

    def get_context_data(self, **kwargs):
        context = super(PressView, self).get_context_data(**kwargs)
        files_folder, _ = Folder.objects.get_or_create(name="Press files")
        context['files'] = files_folder.files
        photos_folder, _ = Folder.objects.get_or_create(name="Press photos")
        context['photos'] = photos_folder.files
        return context

press_view = PressView.as_view()


class PhotoGalleryView(ListView):
    template_name = "photo-gallery.html"
    context_object_name = "photos"

    def get_queryset(self):
        photos_folder, _ = Folder.objects.get_or_create(name="Gallery photos")
        return photos_folder.files

gallery_view = PhotoGalleryView.as_view()
