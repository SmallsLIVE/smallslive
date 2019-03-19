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
from oscar.apps.order.models import Line
from django.db.models import F, Q, Max
from custom_stripe.models import CustomerDetail


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
    template = 'catalogue/album-list.html'
    artist_id = request.GET.get('artist', '')
    if artist_id:
        artist = Artist.objects.filter(pk=artist_id).first()
        album_list = artist.albums()
        artist_page = True
    else:
        album_list =  Product.objects.filter(product_class__name="Album")
        artist_page = False
    paginator = Paginator(album_list, 12)
    page = int(request.GET.get('page', 1))
    album_page = paginator.page(page)
    temp = render_to_string(
        template,
        {'album_page': album_page, 'pagenumber': page, 'artist_page': artist_page},
        context_instance=RequestContext(request))

    data = {
        'template': temp, 'last_page': paginator.num_pages == page
    }

    return JsonResponse(data)


class PurchasedProductsInfoMixin():

    def __init__(self):

        self.digital_album_list = []
        self.physical_album_list = []
        self.track_list = []
        self.album_list = []

    def get_purchased_products(self):
        """ Retrieve products purchased by current user:
            Tracks, CD, or Digital HD. Info comes from the order lines.
            Set up a list of all Albums with Tracks bought.
            CD and HD gives access to all Tracks.

        """
        if not self.request.user.is_authenticated():
            self.album_list = []
        else:
            if False:
                self.digital_album_list = Line.objects.select_related(
                    'product', 'stockrecord', 'product__event', 'product__album').filter(
                    product__product_class__slug='digital-album').distinct('stockrecord')
                self.physical_album_list = Line.objects.select_related(
                    'product', 'stockrecord', 'product__event', 'product__album').filter(
                    product__product_class__slug='physical-album').distinct('stockrecord')
                self.track_list = Line.objects.select_related(
                    'product', 'stockrecord', 'product__event', 'product__album').filter(
                    product__product_class__slug='track').distinct('stockrecord')
            else:
                self.digital_album_list = Line.objects.select_related(
                    'product', 'stockrecord', 'product__event', 'product__album').filter(
                    product__product_class__slug='digital-album',
                    order__user=self.request.user).distinct('stockrecord')
                self.physical_album_list = Line.objects.select_related(
                    'product', 'stockrecord', 'product__event', 'product__album').filter(
                    product__product_class__slug='physical-album',
                    order__user=self.request.user).distinct('stockrecord')
                self.track_list = Line.objects.select_related(
                    'product', 'stockrecord', 'product__event', 'product__album').filter(
                    product__product_class__slug='track',
                    order__user=self.request.user).distinct('stockrecord')

            self.album_list = []
            for album in list(self.digital_album_list) + list(self.physical_album_list):
                album_info = {
                    'parent': album.product.parent,
                    'bought_tracks': [track.pk for track in album.product.parent.tracks.all()],
                    'album_type': 'full_album',
                }
                # Avoid duplicates
                album = [a for a in self.album_list if a['parent'] == album.product.parent]
                if not album:
                    self.album_list.append(album_info)

            # Iterate tracks and accumulate for album
            for track in self.track_list:
                # Search album_list to see if already in list
                # Find the position of the album in the list, if it exists
                albums_matched = [a for a in enumerate(self.album_list)
                                  if a[1]['parent'] == track.product.album]
                if albums_matched:
                    index = albums_matched[0][0]
                    # Add the track to purchased tracks it's not there already.
                    album = albums_matched[0][1]
                    bought_tracks = album['bought_tracks']
                    if track.product.pk not in bought_tracks:
                        bought_tracks.append(track.product.pk)
                        # Update the bought track.
                        self.album_list[index]['bought_tracks'] = bought_tracks
                else:
                    album_info = {
                        'parent': track.product.album,
                        'bought_tracks': [track.product.pk],
                        'album_type': 'track_album',
                    }
                    self.album_list.append(album_info)

                self.album_list = sorted(self.album_list, key=lambda k: k['parent'].title)


class ProductDetailView(catalogue_views.ProductDetailView, PurchasedProductsInfoMixin):

    def get_context_data(self, **kwargs):
        ctx = super(ProductDetailView, self).get_context_data(**kwargs)
        self.get_purchased_products()
        ctx['reviews'] = self.get_reviews()
        ctx['alert_form'] = self.get_alert_form()
        ctx['artist_with_media'] = Artist.objects.exclude(artistproduct=None)
        ctx['has_active_alert'] = self.get_alert_status()
        ctx['is_catalogue'] = True
        if self.request.user.is_authenticated():
            customer_detail = CustomerDetail.get(id=self.request.user.customer.stripe_id)
            if customer_detail:
                ctx['active_card'] = customer_detail.active_card

        if self.object.get_product_class().slug == 'album':
            album_product = Product.objects.filter(pk=self.object.pk ).first()
            ctx['album_product'] = album_product
            track_album = next((item for item in self.album_list if item['parent'] == self.object), None)
            ctx['bought_tracks'] = None
            if track_album:
                ctx['bought_tracks'] = track_album["bought_tracks"]
            ctx['mp3_available'] = album_product.tracks.filter(stockrecords__is_hd=False).count() > 0
            variant = Product.objects.filter(parent=album_product, product_class__slug__in=[
                'physical-album',
                'digital-album'
            ]).first()
            
            if variant.product_class.slug == 'digital-album':
                for album in self.album_list:
                    if self.object.pk == album["parent"].pk:
                        ctx['is_full'] = "full_album"
            ctx['child_product'] = variant

        # Clean basket
        # self.request.basket.flush()

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


