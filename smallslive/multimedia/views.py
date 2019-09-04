import json
import ast
from braces.views import LoginRequiredMixin
from cacheops import cached, cached_view
from django.db.models import F, Q, Max
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, TemplateView, View
from django_thumbor import generate_url
from oscar.apps.order.models import Line
from metrics.models import UserVideoMetric
from oscar_apps.catalogue.models import Product
from oscar_apps.catalogue.views import PurchasedProductsInfoMixin
from custom_stripe.models import CustomerDetail
from events.models import Recording, Event
from .forms import TrackFileForm
from .models import ImageMediaFile, MediaFile


def json_error_response(error_message):
    return HttpResponse(json.dumps(dict(success=False,
                                        error_message=error_message)))


def update_media_viewcount(request):
    if not request.is_ajax():
        raise Http404()

    if request.method == "GET":
        return json_error_response("Only POST requests.")

    recording_id = request.POST.get('recording_id')

    try:
        recording = Recording.objects.get(id=recording_id)
    except:
        return Http404("Recording with that ID not found")

    recording.view_count = F('view_count') + 1
    recording.save()

    response = json.dumps({'status': True})
    return HttpResponse(response, content_type="application/json")


class MostPopularVideos(ListView):
    context_object_name = "events"
    template_name = "multimedia/most_popular_list.html"

    def get_queryset(self):
        @cached(timeout=6*60*60)
        def _get_most_popular_videos():
            most_popular_video_ids = UserVideoMetric.objects.most_popular_video(count=20)
            most_popular_video = []
            for event_data in most_popular_video_ids:
                try:
                    event = Event.objects.filter(id=event_data['event_id']).annotate(
                        added=Max('recordings__date_added')).first()
                    most_popular_video.append({'event': event, 'play_count': event_data['count']})
                except Event.DoesNotExist:
                    pass
            return most_popular_video
        return _get_most_popular_videos()
    
    def get_context_data(self, **kwargs):
        context = super(MostPopularVideos, self).get_context_data(**kwargs)
        context['most_popular_videos'] = True
        context['cache_name'] = 'most_popular_videos'
        return context

most_popular_videos = MostPopularVideos.as_view()


class MostPopularWeeklyVideos(ListView):
    context_object_name = "events"
    template_name = "multimedia/most_popular_list.html"

    def get_queryset(self):
        @cached(timeout=6*60*60)
        def _get_most_popular_videos():
            most_popular_video_ids = UserVideoMetric.objects.most_popular_video(count=20, weekly=True)
            most_popular_video = []
            for event_data in most_popular_video_ids:
                try:
                    event = Event.objects.filter(id=event_data['event_id']).annotate(
                        added=Max('recordings__date_added')).first()
                    most_popular_video.append({'event': event, 'play_count': event_data['count']})
                except Event.DoesNotExist:
                    pass
            return most_popular_video
        return _get_most_popular_videos()

    def get_context_data(self, **kwargs):
        context = super(MostPopularWeeklyVideos, self).get_context_data(**kwargs)
        context['most_popular_weekly_videos'] = True
        context['cache_name'] = 'most_popular_videos'
        return context

most_popular_weekly_videos = MostPopularWeeklyVideos.as_view()


class MostRecentVideos(ListView):
    context_object_name = "events"
    queryset = Event.objects.most_recent_video()[:30]
    template_name = "multimedia/most_recent_list.html"

    def get_context_data(self, **kwargs):
        context = super(MostRecentVideos, self).get_context_data(**kwargs)
        context['most_recent_videos'] = True
        return context

most_recent_videos = MostRecentVideos.as_view()


class MostPopularAudio(ListView):
    context_object_name = "events"
    template_name = "multimedia/most_popular_list.html"

    def get_queryset(self):
        @cached(timeout=6*60*60)
        def _get_most_popular_audio():
            most_popular_audio_ids = UserVideoMetric.objects.most_popular_audio(count=20)
            most_popular_audio = []
            for event_data in most_popular_audio_ids:
                try:
                    event = Event.objects.filter(id=event_data['event_id']).annotate(
                        added=Max('recordings__date_added')).first()
                    most_popular_audio.append({'event': event, 'play_count': event_data['count']})
                except Event.DoesNotExist:
                    pass
            return most_popular_audio
        return _get_most_popular_audio()

    def get_context_data(self, **kwargs):
        context = super(MostPopularAudio, self).get_context_data(**kwargs)
        context['most_popular_audio'] = True
        context['cache_name'] = 'most_popular_audio'
        return context

most_popular_audio = MostPopularAudio.as_view()


class MostPopularWeeklyAudio(ListView):
    context_object_name = "events"
    template_name = "multimedia/most_popular_list.html"

    def get_queryset(self):
        @cached(timeout=6*60*60)
        def _get_most_popular_audio():
            most_popular_audio_ids = UserVideoMetric.objects.most_popular_audio(count=20, weekly=True)
            most_popular_audio = []
            for event_data in most_popular_audio_ids:
                try:
                    event = Event.objects.filter(id=event_data['event_id']).annotate(
                        added=Max('recordings__date_added')).first()
                    most_popular_audio.append({'event': event, 'play_count': event_data['count']})
                except Event.DoesNotExist:
                    pass
            return most_popular_audio
        return _get_most_popular_audio()

    def get_context_data(self, **kwargs):
        context = super(MostPopularWeeklyAudio, self).get_context_data(**kwargs)
        context['most_popular_weekly_audio'] = True
        context['cache_name'] = 'most_popular_audio'
        return context

most_popular_weekly_audio = MostPopularWeeklyAudio.as_view()


class MostRecentAudio(ListView):
    context_object_name = "events"
    queryset = Event.objects.most_recent_audio()[:30]
    template_name = "multimedia/most_recent_list.html"

    def get_context_data(self, **kwargs):
        context = super(MostRecentAudio, self).get_context_data(**kwargs)
        context['most_recent_audio'] = True
        return context

most_recent_audio = MostRecentAudio.as_view()


def media_redirect(request, recording_id):
    recording = get_object_or_404(Recording, id=recording_id)
    media_file = recording.media_file
    if media_file.media_type == "audio":
        url = media_file.get_file_url()
    else:
        url = media_file.get_sd_video_url()
    return redirect(url)


class UploadTrackView(CreateView):
    model = MediaFile
    form_class = TrackFileForm

    def post(self, request, *args, **kwargs):
        super(UploadTrackView, self).post(request, *args, **kwargs)
        return HttpResponse(self.object.id)

    def get_form_kwargs(self):
        kwargs = super(UploadTrackView, self).get_form_kwargs()
        kwargs['category'] = self.kwargs.get('category')
        return kwargs

    def get_success_url(self):
        return ""

upload_track = UploadTrackView.as_view()


class UploadImagePreview(View):

    def post(self, *args, **kwargs):
        image = self.request.FILES['photo']
        image_file = ImageMediaFile.objects.create(photo=image)

        filters = {
            'height': 300,
            'width': 300,
            'smart': True,
        }
        url = generate_url(image_url=image_file.photo.url, **filters)

        data = {
            'success': True,
            'src': url,
            'id': image_file.pk
        }
        response = json.dumps(data)

        return HttpResponse(response, content_type="application/json")



upload_image_preview = UploadImagePreview.as_view()


class MyDownloadsView(LoginRequiredMixin, ListView):
    context_object_name = 'lines'
    template_name = 'multimedia/new-downloads.html'

    def get_queryset(self):
        return Line.objects.select_related('product', 'stockrecord', 'product__event', 'product__album').filter(Q(
            product__product_class__slug='track') | Q(product__product_class__slug='digital-album'),
            order__user=self.request.user).distinct('stockrecord')

my_downloads = MyDownloadsView.as_view()


class NewMyDownloadsView(LoginRequiredMixin, ListView, PurchasedProductsInfoMixin):
    context_object_name = 'lines'
    template_name = 'multimedia/library.html'

    def get_queryset(self):
        return Line.objects.select_related('product', 'stockrecord', 'product__event', 'product__album').filter(
            product__product_class__slug__in=['digital-album', 'physical-album', 'track'],
            order__user=self.request.user).distinct('stockrecord')

    def get_context_data(self, **kwargs):
        context = super(NewMyDownloadsView, self).get_context_data(**kwargs)
        self.get_purchased_products()

        context['album_list'] = self.album_list
        print context['album_list']
        return context

new_downloads = NewMyDownloadsView.as_view()


class AlbumView(TemplateView):
    """
    To be called from AJAX (Library).
    """
    model = Product
    pk_url_kwarg = 'pk'
    template_name = 'multimedia/album-display.html'
    context_object_name = 'album_product'

    def get_context_data(self, **kwargs):
        context = super(AlbumView, self).get_context_data(**kwargs)

        context['library'] = True
        bought_tracks = self.request.GET.get('bought_tracks', '[]')
        context['bought_tracks'] = ast.literal_eval(bought_tracks)
        context['is_full'] = self.request.GET.get('album_type', '')
        album_product = Product.objects.filter(pk=self.request.GET.get('productId', '')).first()
        context['album_product'] = album_product
        variant = Product.objects.filter(parent=album_product, product_class__slug__in=[
            'physical-album',
            'digital-album'
        ]).first()
        context['mp3_available'] = album_product.tracks.filter(stockrecords__is_hd=False).count() > 0
        context['child_product'] = variant
        customer_detail = CustomerDetail.get(id=self.request.user.customer.stripe_id)
        if customer_detail:
            context['active_card'] = customer_detail.active_card
        print context['bought_tracks']

        return context

album_view = AlbumView.as_view()


class AddTracksView(TemplateView):
    template_name = 'multimedia/basket-items.html'

    def get_context_data(self, **kwargs):

        tracks = self.request.GET.getlist('trackId', [])
        products = Product.objects.filter(pk__in=tracks)
        context = super(AddTracksView, self).get_context_data(**kwargs)
        context['products'] = products

        customer_detail = CustomerDetail.get(id=self.request.user.customer.stripe_id)
        context['active_card'] = customer_detail.active_card

        return context

add_tracks = AddTracksView.as_view()
