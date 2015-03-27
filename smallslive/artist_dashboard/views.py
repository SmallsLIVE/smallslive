from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
import artists.views as artist_views
from events.models import Recording
import events.views as event_views
from .forms import ToggleRecordingStateForm, EventEditForm


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
        artist = self.request.user.artist
        context['upcoming_events'] = artist.events.upcoming()[:5]
        return context

dashboard = DashboardView.as_view()


class EditProfileView(artist_views.ArtistEditView):
    template_name = 'artist_dashboard/edit_profile.html'

    def get_object(self, queryset=None):
        return self.request.user.artist

    def test_func(self, user):
        return True

edit_profile = EditProfileView.as_view()


class EventDetailView(event_views.EventDetailView):
    template_name = 'artist_dashboard/event_detail.html'

event_detail = EventDetailView.as_view()


class EventEditView(event_views.EventEditView):
    form_class = EventEditForm
    template_name = 'artist_dashboard/event_edit.html'

event_edit = EventEditView.as_view()


class ToggleRecordingStateView(UpdateView):
    form_class = ToggleRecordingStateForm
    model = Recording
    success_url = '/'

    def form_valid(self, form):
        super(ToggleRecordingStateView, self).form_valid(form)
        return HttpResponse(status=204)

    def form_invalid(self, form):
        super(ToggleRecordingStateView, self).form_invalid(form)
        return HttpResponse(status=400)

toggle_recording_state = ToggleRecordingStateView.as_view()
