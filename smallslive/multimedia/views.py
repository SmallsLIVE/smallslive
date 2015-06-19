import json
from django.db.models import F
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView
from events.models import Recording
from multimedia.models import MediaFile


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
    context_object_name = "recordings"
    queryset = Recording.objects.video().most_popular()[:30]
    template_name = "multimedia/archive-list.html"
    
    def get_context_data(self, **kwargs):
        context = super(MostPopularVideos, self).get_context_data(**kwargs)
        context['most_popular_videos'] = True
        return context

most_popular_videos = MostPopularVideos.as_view()


class MostRecentVideos(ListView):
    context_object_name = "recordings"
    queryset = Recording.objects.video().most_recent()[:30]
    template_name = "multimedia/archive-list.html"

    def get_context_data(self, **kwargs):
        context = super(MostRecentVideos, self).get_context_data(**kwargs)
        context['most_recent_videos'] = True
        return context

most_recent_videos = MostRecentVideos.as_view()


class MostPopularAudio(ListView):
    context_object_name = "recordings"
    queryset = Recording.objects.audio().most_popular()[:30]
    template_name = "multimedia/archive-list.html"

    def get_context_data(self, **kwargs):
        context = super(MostPopularAudio, self).get_context_data(**kwargs)
        context['most_popular_audio'] = True
        return context

most_popular_audio = MostPopularAudio.as_view()


class MostRecentAudio(ListView):
    context_object_name = "recordings"
    queryset = Recording.objects.audio().most_recent()[:30]
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
    fields = ('file',)

    def post(self, request, *args, **kwargs):
        super(UploadTrackView, self).post(request, *args, **kwargs)
        return HttpResponse(self.object.id)

    def get_success_url(self):
        return ""

upload_track = UploadTrackView.as_view()
