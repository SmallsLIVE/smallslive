from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from allauth.account.forms import ChangePasswordForm
import allauth.account.views as allauth_views
import artists.views as artist_views

from events.models import Recording
import events.views as event_views
import users.forms as user_forms
from users.models import LegalAgreementAcceptance
from users.views import HasArtistAssignedMixin
from .forms import ToggleRecordingStateForm, EventEditForm, ArtistInfoForm, EditProfileForm


class MyGigsView(ListView):
    context_object_name = 'gigs'
    paginate_by = 15
    template_name = 'artist_dashboard/my_gigs.html'

    def get_context_data(self, **kwargs):
        context = super(MyGigsView, self).get_context_data(**kwargs)
        paginator = context['paginator']
        page = paginator.page(self.kwargs.get('page', 1))
        adjacent_pages = 2
        startPage = max(page.number - adjacent_pages, 1)
        if startPage <= 3:
            startPage = 1
        endPage = page.number + adjacent_pages + 1
        if endPage >= paginator.num_pages - 1:
            endPage = paginator.num_pages + 1
        page_numbers = [n for n in xrange(startPage, endPage) if n > 0 and n <= paginator.num_pages]
        context.update({
            'page_numbers': page_numbers,
            'show_first': 1 not in page_numbers,
            'show_last': paginator.num_pages not in page_numbers,
            })

        return context

    def get_queryset(self):
        artist = self.request.user.artist
        queryset = artist.gigs_played.select_related('event')
        queryset = self.apply_filters(queryset).order_by('-event__start')
        return queryset

    def apply_filters(self, queryset):
        audio_filter = self.request.GET.get('audio_filter')
        video_filter = self.request.GET.get('video_filter')
        leader_filter = self.request.GET.get('leader_filter')
        if audio_filter and audio_filter in Recording.FILTER_STATUS:
            if audio_filter == 'None':
                queryset = queryset.exclude(event__recordings__media_file__media_type='audio')
            elif audio_filter == Recording.STATUS.Hidden:
                queryset = queryset.filter(event__recordings__media_file__media_type='audio',
                                           event__recordings__state=Recording.STATUS.Hidden)
            elif audio_filter == Recording.STATUS.Published:
                queryset = queryset.filter(event__recordings__media_file__media_type='audio',
                                           event__recordings__state=Recording.STATUS.Published)
        if video_filter and video_filter in Recording.FILTER_STATUS:
            if video_filter == 'None':
                queryset = queryset.exclude(event__recordings__media_file__media_type='video')
            elif video_filter == Recording.STATUS.Hidden:
                queryset = queryset.filter(event__recordings__media_file__media_type='video',
                                           event__recordings__state=Recording.STATUS.Hidden)
            elif video_filter == Recording.STATUS.Published:
                queryset = queryset.filter(event__recordings__media_file__media_type='video',
                                           event__recordings__state=Recording.STATUS.Published)
        if leader_filter:
            if leader_filter == 'true':
                queryset = queryset.filter(is_leader=True)
            else:
                queryset = queryset.filter(is_leader=False)

        return queryset.distinct()

my_gigs = MyGigsView.as_view()


class DashboardView(HasArtistAssignedMixin, TemplateView):
    template_name = 'artist_dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        artist = self.request.user.artist
        context['upcoming_events'] = artist.gigs_played.upcoming().select_related('event', 'artist')[:5]
        context['first_time'] = self.request.session.get('first_time', 'true')
        return context

    def get(self, request, *args, **kwargs):
        # check if this is the users first time on the dashboard, and if it is,
        # set a variable in the template so that intro.js widget can start
        response = super(DashboardView, self).get(request, *args, **kwargs)
        if not request.session.get('first_time'):
            request.session['first_time'] = 'false'
        return response

dashboard = DashboardView.as_view()


class EditProfileView(artist_views.ArtistEditView):
    form_class = EditProfileForm
    template_name = 'artist_dashboard/edit_profile.html'

    def get_object(self, queryset=None):
        return self.request.user.artist

    def test_func(self, user):
        return True

edit_profile = EditProfileView.as_view()


class EventDetailView(event_views.EventDetailView):
    template_name = 'artist_dashboard/event_detail.html'

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        context['is_leader'] = self.request.user.artist.is_leader_for_event(self.object)
        context['audio'] = self.object.recordings.audio()
        context['video'] = self.object.recordings.video()
        return context

event_detail = EventDetailView.as_view()


class EventEditView(event_views.EventEditView):
    form_class = EventEditForm
    template_name = 'artist_dashboard/event_edit.html'

    def get_context_data(self, **kwargs):
        context = super(EventEditView, self).get_context_data(**kwargs)
        context['is_leader'] = self.request.user.artist.is_leader_for_event(self.object)
        context['audio'] = self.object.recordings.audio()
        context['video'] = self.object.recordings.video()
        return context

event_edit = EventEditView.as_view()


class ToggleRecordingStateView(UpdateView):
    form_class = ToggleRecordingStateForm
    model = Recording
    success_url = '/'

    def form_valid(self, form):
        super(ToggleRecordingStateView, self).form_valid(form)
        return HttpResponse(status=204)

    def form_invalid(self, form):
        super(ToggleRecordingStateView, self).form_invalid(form)
        return HttpResponse(status=400)

toggle_recording_state = ToggleRecordingStateView.as_view()


def legal(request):
    user_signed = LegalAgreementAcceptance.objects.filter(user=request.user).exists()
    if not user_signed and 'sign-agreement' in request.POST:
        LegalAgreementAcceptance.objects.create(user=request.user)
        user_signed = True
        messages.success(request, "You've successfully signed the artist agreement.")
    return render(request, 'artist_dashboard/legal.html', {
        'user_signed': user_signed
    })


def artist_settings(request):
    # if this is a POST request we need to process the form data
    if 'artist_info' in request.POST:
        # create a form instance and populate it with data from the request:
        artist_info_form = ArtistInfoForm(data=request.POST, instance=request.user)
        # check whether it's valid:
        if artist_info_form.is_valid():
            artist_info_form.save(request)
            messages.success(request, "You've successfully updated your profile.")
            return redirect('artist_dashboard:settings')
    # if a GET (or any other method) we'll create a blank form
    else:
        artist_info_form = ArtistInfoForm(instance=request.user)

    if 'change_email' in request.POST:
        change_email_form = user_forms.ChangeEmailForm(data=request.POST, user=request.user)
        if change_email_form.is_valid():
            change_email_form.save(request)
            messages.success(request, 'Your email address has been changed successfully.')
            return redirect('account_email_verification_sent')
    else:
        change_email_form = user_forms.ChangeEmailForm(user=request.user)

    if 'change_password' in request.POST:
        change_password_form = ChangePasswordForm(data=request.POST, user=request.user)
        if change_password_form.is_valid():
            change_password_form.save()
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('artist_dashboard:settings')
    else:
        change_password_form = ChangePasswordForm(user=request.user)

    return render(request, 'artist_dashboard/settings.html', {
        'change_email_form': change_email_form,
        'artist_info_form': artist_info_form,
        'change_password_form': change_password_form,
    })


class DashboardLoginView(allauth_views.LoginView):
    success_url = reverse_lazy('artist_dashboard:home')
    template_name = 'artist_dashboard/login.html'

    def get_authenticated_redirect_url(self):
        return reverse('artist_dashboard:home')

login = DashboardLoginView.as_view()
