from django.views.generic import TemplateView, ListView
from filer.models import File, Folder


class PressView(TemplateView):
    template_name = "press.html"

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
