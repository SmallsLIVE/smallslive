from django.views.generic import TemplateView
from filer.models import File, Folder


class PressView(TemplateView):
    template_name = "press.html"

    def get_context_data(self, **kwargs):
        context = super(PressView, self).get_context_data(**kwargs)
        context['files'] = Folder.objects.get(name="Press files").files
        context['photos'] = Folder.objects.get(name="Press photos").files
        return context

press_view = PressView.as_view()
