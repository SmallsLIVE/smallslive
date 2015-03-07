from django.contrib.flatpages.models import FlatPage
from django.views.generic import TemplateView, ListView, DetailView
from filer.models import File, Folder


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
