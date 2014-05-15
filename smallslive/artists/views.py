from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from braces.views import LoginRequiredMixin, UserPassesTestMixin
from .forms import ArtistAddForm
from .models import Artist


class ArtistAddView(CreateView):
    model = Artist
    form_class = ArtistAddForm
    template_name = 'artists/artist_add.html'

artist_add = ArtistAddView.as_view()


class ArtistEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Artist
    form_class = ArtistAddForm
    template_name = 'artists/artist_edit.html'

    def test_func(self, user):
        """
        Show 403 forbidden page only when the logged in user doesn't have required
        permissions, redirect anonymous users to the login screen.
        """
        self.raise_exception = True
        try:
            artist_id_match = self.kwargs.get('pk') == str(user.artist.id)
        except Artist.DoesNotExist:
            artist_id_match = False
        return (artist_id_match or user.is_superuser)

artist_edit = ArtistEditView.as_view()


class ArtistDetailView(DetailView):
    model = Artist
    context_object_name = 'artist'

artist_detail = ArtistDetailView.as_view()


def artist_instrument_ajax(request, pk):
    instrument = Artist.objects.get(pk=pk).instruments.first()
    instrument_id = getattr(instrument, 'id', "")
    return HttpResponse(instrument_id)
