import itertools
from oscar_apps.catalogue.models import Product
from artists.models import Artist
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template import RequestContext
from django.template.loader import render_to_string
from oscar.apps.catalogue import views as catalogue_views
from oscar_apps.catalogue.models import Product, UserCatalogue, UserCatalogueProduct
from oscar.apps.catalogue.views import ProductCategoryView
from artists.models import Artist
from .mixins import ProductMixin


class ProductCategoryView(catalogue_views.ProductCategoryView):
    def get_context_data(self, **kwargs):
        context = super(ProductCategoryView, self).get_context_data(**kwargs)
        context['featured_product'] = Product.objects.filter(featured=True, categories__in=self.get_categories()).first()
        return context


class ArtistCatalogue(ProductCategoryView):

    def get(self, request, *args, **kwargs):
        id = request.GET.get('id', None)

        artist = Artist.objects.filter(pk=id).first()
        context = {'artist': artist}
        template = 'catalogue/artist-category.html'

        temp = render_to_string(template,
                                context
                                )

        data = {
            'template': temp
        }

        return JsonResponse(data)


def get_album_catalog(request):
    template = 'catalogue/album-list.html'
    artist_id = request.GET.get('artist', '')
    if artist_id:
        artist = Artist.objects.filter(pk=artist_id).first()
        album_list = artist.albums()
        artist_page = True
    else:
        album_list = Product.objects.filter(
            product_class__name='Album').order_by('upc')
        artist_page = False
    paginator = Paginator(album_list, 12)
    page = int(request.GET.get('page', 1))
    album_page = paginator.page(page)
    temp = render_to_string(
        template,
        {'album_page': album_page, 'pagenumber': page, 'artist_page': artist_page})

    data = {
        'template': temp, 'last_page': paginator.num_pages == page
    }

    return JsonResponse(data)


# @TODO : Fix later 
class CatalogueView(catalogue_views.CatalogueView):
    template_name = 'catalogue/index/home.html'
    def get_context_data(self, **kwargs):
        context = super(CatalogueView, self).get_context_data(**kwargs)
        context['newest_recordings'] = list(Product.objects.filter(
            product_class__slug="full-access")) + list(Product.objects.filter(
            product_class__slug="album").order_by('-id')[:12])
        context['all_recordings'] = Product.objects.filter(
            product_class__slug="album").order_by('upc')[:12]
        context['featured_recordings'] = Product.objects.filter(
            product_class__slug="album", featured=True)[:4]
        context['preview_track_id_counter'] = itertools.count()
        context['artist_with_media'] = Artist.objects.exclude(artistproduct=None)
        context['is_catalogue_list'] = True

        return context


class ProductDetailView(catalogue_views.ProductDetailView, ProductMixin):

    def can_preview(self, track_list):
        if not track_list:
            return False

        for track in track_list:
            if track.get_track_preview_url() != "blank.mp3":
                return True
        return False

    def get_context_data(self, **kwargs):

        ctx = super(ProductDetailView, self).get_context_data(**kwargs)

        # We need to clear the basket.
        # Probably do this in a middleware so it's global?
        self.request.basket.flush()

        # Set the flow type for checkout flow
        ctx['flow_type'] = 'catalog_selection'

        self.get_purchased_products()
        self.get_products()
        ctx['artist_with_media'] = Artist.objects.exclude(artistproduct=None)
        ctx['is_catalogue'] = True
        ctx['comma_separated_leaders'] = self.comma_separated_leaders
        total_donation = 0
        ctx['album_product'] = self.album_product
        if self.object.get_product_class().slug == 'album':
            if self.request.user.is_authenticated():
                total_donation = self.request.user.get_project_donation_amount(self.album_product.pk)
            ctx['total_donation'] = total_donation
            track_album = next((item for item in self.album_list if item['parent'] == self.object), None)
            ctx['is_bought'] = False
            if track_album:
                ctx['is_bought'] = True
            ctx['mp3_available'] = self.album_product.tracks.filter(stockrecords__is_hd=False).count() > 0
            ctx['child_product'] = self.child_product

        ctx['can_preview'] = self.can_preview(self.album_product.get_tracks())

        # Clean basket
        self.request.basket.flush()

        return ctx

    def get_template_names(self):
        """
        Return a list of possible templates.

        If an overriding class sets a template name, we use that. Otherwise,
        we try 2 options before defaulting to catalogue/detail.html:
            1). detail-for-upc-<upc>.html
            2). detail-for-class-<classname>.html

        This allows alternative templates to be provided for a per-product
        and a per-item-class basis.
        """
        if self.object.get_product_class().slug == 'album':
            return ['multimedia/store-album.html']

        if self.template_name:
            return [self.template_name]

        return [
            '%s/detail-for-upc-%s.html' % (
                self.template_folder, self.object.upc),
            '%s/detail-for-class-%s.html' % (
                self.template_folder, self.object.get_product_class().slug),
            '%s/detail.html' % (self.template_folder)]
