import json
from braces.views import LoginRequiredMixin
from cacheops import cached, cached_view
from django.db.models import F, Q, Max
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView
from metrics.models import UserVideoMetric
from oscar.apps.order.models import Line
from events.models import Recording, Event
from .forms import TrackFileForm
from .models import MediaFile


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


class MyDownloadsView(LoginRequiredMixin, ListView):
    context_object_name = 'lines'
    template_name = 'multimedia/new-downloads.html'

    def get_queryset(self):
        return Line.objects.select_related('product', 'stockrecord', 'product__event', 'product__album').filter(Q(
            product__product_class__slug='track') | Q(product__product_class__slug='digital-album'),
            order__user=self.request.user).distinct('stockrecord')

my_downloads = MyDownloadsView.as_view()

class NewMyDownloadsView(LoginRequiredMixin, ListView):
    context_object_name = 'lines'
    template_name = 'multimedia/library.html'

    def get_queryset(self):
        return Line.objects.select_related('product', 'stockrecord', 'product__event', 'product__album').filter(Q(
            product__product_class__slug='track') | Q(product__product_class__slug='digital-album'),
            order__user=self.request.user).distinct('stockrecord')

new_downloads = NewMyDownloadsView.as_view()
