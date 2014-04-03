from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from .models import Artist


class ArtistAddView(CreateView):
    model = Artist
    template_name = 'artists/artist_add.html'
    fields = ('first_name', 'last_name', 'salutation', 'artist_type', 'biography', 'website', 'photo')

artist_add = ArtistAddView.as_view()


class ArtistEditView(UpdateView):
    model = Artist
    template_name = 'artists/artist_edit.html'
    fields = ('first_name', 'last_name', 'salutation', 'artist_type', 'biography', 'website', 'photo')

artist_edit = ArtistEditView.as_view()


class ArtistDetailView(DetailView):
    model = Artist
    context_object_name = 'artist'

artist_detail = ArtistDetailView.as_view()
