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
