from django.http import Http404
from django.shortcuts import render

# URL redirects from old site
from django.views.generic import RedirectView
from rest_framework.reverse import reverse
from artists.models import Artist


class OldSiteRedirectView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        if self.request.GET.get('itemCategory') == '43178' or  self.request.GET.get('itemcategory') == '43178':
            return reverse('contact-and-info')
        elif self.request.GET.get('itemCategory') == '43179' or self.request.GET.get('itemcategory') == '43179':
            return reverse('live-stream')
        elif self.request.GET.get('itemCategory') == '32321' or self.request.GET.get('itemcategory') == '32321':
            return reverse('live-stream')
        elif (self.request.GET.get('itemCategory') == '61473' or self.request.GET.get('itemcategory') == '61473') \
                and self.request.GET.get('personDetailId'):
            try:
                artist_id = self.request.GET.get('personDetailId')
                if "'" in  artist_id:
                    artist_id = artist_id.split('')[0]
                artist = Artist.objects.get(id=int(artist_id))
            except (TypeError, ValueError, Artist.DoesNotExist) as e:
                raise Http404("Can't find the artist")
            return artist.get_absolute_url()
        return reverse('home')
