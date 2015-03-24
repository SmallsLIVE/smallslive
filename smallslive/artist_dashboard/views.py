from django.views.generic import TemplateView
from django.views.generic.list import ListView
from events.models import Event


class MyGigsView(ListView):
    context_object_name = 'events'
    paginate_by = 15
    template_name = 'artist_dashboard/my_gigs.html'

    def get_queryset(self):
        artist = self.request.user.artist
        return artist.events.all()

my_gigs = MyGigsView.as_view()


class DashboardView(TemplateView):
    template_name = 'artist_dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['upcoming_events'] = Event.upcoming.all()[:5]
        return context

dashboard = DashboardView.as_view()
