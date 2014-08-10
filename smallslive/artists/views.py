from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.detail import DetailView
from braces.views import LoginRequiredMixin, UserPassesTestMixin
from .forms import ArtistAddForm, ArtistInviteForm
from .models import Artist


def artist_add(request):
    if request.method == 'POST':
        artist_add_form = ArtistAddForm(request.POST)
        artist_invite_form = ArtistInviteForm(request.POST)
        forms = [artist_add_form, artist_invite_form]
        if all([form.is_valid() for form in forms]):
            artist = artist_add_form.save()
            email = artist_invite_form.cleaned_data.get('email')
            invite_type = artist_invite_form.cleaned_data.get('invite_type')
            if invite_type == ArtistInviteForm.INVITE_TYPE.standard_invite:
                artist.send_invitation(request, email)
            elif invite_type == ArtistInviteForm.INVITE_TYPE.custom_invite:
                artist.send_invitation(request, email, artist_invite_form.cleaned_data.get('invite_text'))
            messages.success(request, "Artist {0} successfully added!".format(artist.full_name()))
            return redirect('artist_add')
    else:
        artist_add_form = ArtistAddForm()
        artist_invite_form = ArtistInviteForm()

    return render(request, 'artists/artist_add.html', {
        'artist_add_form': artist_add_form,
        'artist_invite_form': artist_invite_form
    })


# note - this is here only for Mezzrow compatibility
class ArtistAddView(CreateView):
    model = Artist
    form_class = ArtistAddForm
    template_name = 'artists/artist_add.html'


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
