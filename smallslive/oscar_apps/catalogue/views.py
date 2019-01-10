from artists.models import Artist
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render
from oscar.apps.catalogue import views as catalogue_views
from oscar_apps.catalogue.models import Product
from oscar.apps.catalogue.views import ProductCategoryView


class ProductCategoryView(catalogue_views.ProductCategoryView):
    def get_context_data(self, **kwargs):
        context = super(ProductCategoryView, self).get_context_data(**kwargs)
        context['featured_product'] = Product.objects.filter(featured=True, categories__in=self.get_categories()).first()
        return context

class ArtistCatalogue(ProductCategoryView):

    def get(self, request, *args, **kwargs):
        id = request.GET.get('id', None)

        artist = Artist.objects.filter(pk=id).first()
        above_limit = artist.albums().count() > 8
        context = {'artist': artist, 'above_limit':above_limit}
        template = 'catalogue/artist-category.html'

        temp = render_to_string(template,
                                context,
                                context_instance=RequestContext(request)
                                )

        data = {
            'template': temp
        }

        return JsonResponse(data)

def get_album_catalog(request):
    artist_id = content=request.GET.get('artist', '')
    if artist_id:
        artist =  Artist.objects.filter(pk=artist_id)
        album_list =  artist.albums
        artist_page = True
    else:
        album_list =  Product.objects.filter(product_class__slug="album")
        artist_page = False
    paginator = Paginator(album_list, 8)
    page = int(request.GET.get('page', 1))
    album_page = paginator.page(page)
    return render(request, 'catalogue/album-list.html', {'album_page': album_page, 'pagenumber':page, 'artist_page':artist_page})