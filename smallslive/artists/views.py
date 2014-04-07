from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from .forms import ArtistAddForm
from .models import Artist


class ArtistAddView(CreateView):
    model = Artist
    form_class = ArtistAddForm
    template_name = 'artists/artist_add.html'

artist_add = ArtistAddView.as_view()


class ArtistEditView(UpdateView):
    model = Artist
    form_class = ArtistAddForm
    template_name = 'artists/artist_edit.html'

artist_edit = ArtistEditView.as_view()


class ArtistDetailView(DetailView):
    model = Artist
    context_object_name = 'artist'

artist_detail = ArtistDetailView.as_view()
