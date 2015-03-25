from django.views.generic import TemplateView
from django.views.generic.list import ListView
from artists.views import ArtistEditView
from events.models import Event


class MyGigsView(ListView):
    context_object_name = 'gigs'
    paginate_by = 15
    template_name = 'artist_dashboard/my_gigs.html'

    def get_queryset(self):
        artist = self.request.user.artist
        return artist.gigs_played.select_related('event').order_by('-event__start')

my_gigs = MyGigsView.as_view()


class DashboardView(TemplateView):
    template_name = 'artist_dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['upcoming_events'] = Event.upcoming.all()[:5]
        return context

dashboard = DashboardView.as_view()


class EditProfileView(ArtistEditView):
    template_name = 'artist_dashboard/edit_profile.html'

    def get_object(self, queryset=None):
        return self.request.user.artist

    def test_func(self, user):
        return True

edit_profile = EditProfileView.as_view()
