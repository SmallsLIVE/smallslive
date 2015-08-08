import json
from braces.views import LoginRequiredMixin
from django.db.models import F, Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView
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
    queryset = Event.objects.most_popular_video()[:30]
    template_name = "multimedia/archive-list.html"
    
    def get_context_data(self, **kwargs):
        context = super(MostPopularVideos, self).get_context_data(**kwargs)
        context['most_popular_videos'] = True
        return context

most_popular_videos = MostPopularVideos.as_view()


class MostRecentVideos(ListView):
    context_object_name = "events"
    queryset = Event.objects.most_recent_video()[:30]
    template_name = "multimedia/archive-list.html"

    def get_context_data(self, **kwargs):
        context = super(MostRecentVideos, self).get_context_data(**kwargs)
        context['most_recent_videos'] = True
        return context

most_recent_videos = MostRecentVideos.as_view()


class MostPopularAudio(ListView):
    context_object_name = "events"
    queryset = Event.objects.most_popular_audio()[:30]
    template_name = "multimedia/archive-list.html"

    def get_context_data(self, **kwargs):
        context = super(MostPopularAudio, self).get_context_data(**kwargs)
        context['most_popular_audio'] = True
        return context

most_popular_audio = MostPopularAudio.as_view()


class MostRecentAudio(ListView):
    context_object_name = "events"
    queryset = Event.objects.most_recent_audio()[:30]
    template_name = "multimedia/archive-list.html"

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
        print kwargs
        return kwargs

    def get_success_url(self):
        return ""

upload_track = UploadTrackView.as_view()


class MyDownloadsView(LoginRequiredMixin, ListView):
    context_object_name = 'lines'
    template_name = 'multimedia/my-downloads.html'

    def get_queryset(self):
        return Line.objects.select_related('product', 'stockrecord', 'product__event', 'product__album').filter(Q(
            product__product_class__slug='track') | Q(product__product_class__slug='digital-album'),
            order__user=self.request.user).distinct('stockrecord')

my_downloads = MyDownloadsView.as_view()
