from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from allauth.account.forms import ChangePasswordForm
import allauth.account.views as allauth_views
from metrics.models import UserVideoMetric

from artists.models import Artist
from events.models import Recording, Event
import events.views as event_views
import users.forms as user_forms
from users.models import LegalAgreementAcceptance
from users.views import HasArtistAssignedMixin
from .forms import ToggleRecordingStateForm, EventEditForm, ArtistInfoForm, EditProfileForm, ArtistResetPasswordForm


class MyGigsView(HasArtistAssignedMixin, ListView):
    context_object_name = 'gigs'
    paginate_by = 15
    template_name = 'artist_dashboard/my_gigs.html'

    def get_context_data(self, **kwargs):
        context = super(MyGigsView, self).get_context_data(**kwargs)
        paginator = context['paginator']
        current_page_number = context['page_obj'].number
        adjacent_pages = 2
        startPage = max(current_page_number - adjacent_pages, 1)
        if startPage <= 3:
            startPage = 1
        endPage = current_page_number + adjacent_pages + 1
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
        artist_event_ids = list(self.request.user.artist.event_id_list())
        context['upcoming_events'] = artist.gigs_played.upcoming().select_related('event', 'artist')[:5]
        context['most_viewed'] = Recording.objects.audio().most_popular().filter(event__performers=artist)[:3]
        context['most_listened_to'] = Recording.objects.video().most_popular().filter(event__performers=artist)[:3]
        context['weekly_artist_stats'] = UserVideoMetric.objects.this_week_counts(artist_event_ids=artist_event_ids,
                                                                                  humanize=True)
        context['monthly_artist_stats'] = UserVideoMetric.objects.this_month_counts_for_artist(
            artist_event_ids=artist_event_ids, humanize=True)
        context['monthly_stats'] = UserVideoMetric.objects.this_month_counts(humanize=True)
        context['weekly_stats'] = UserVideoMetric.objects.this_week_counts(humanize=True)
        context['date_counts'] = UserVideoMetric.objects.date_counts(7, 2015)
        first_login = self.request.user.is_first_login()
        context['first_login'] = first_login
        # don't show intro.js when user reloads the dashboard
        if first_login:
            self.request.user.last_login += timedelta(seconds=1)
            self.request.user.save()
        return context

dashboard = DashboardView.as_view()


class EditProfileView(HasArtistAssignedMixin, UpdateView):
    form_class = EditProfileForm
    model = Artist
    template_name = 'artist_dashboard/edit_profile.html'

    def get_object(self, queryset=None):
        return self.request.user.artist

    def get_success_url(self):
        messages.success(self.request, "You've successfully updated your artist profile.")
        return reverse('artist_dashboard:edit_profile')

edit_profile = EditProfileView.as_view()


class EventDetailView(HasArtistAssignedMixin, event_views.EventDetailView):
    template_name = 'artist_dashboard/event_detail.html'

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        context['is_leader'] = self.request.user.artist.is_leader_for_event(self.object)
        context['audio'] = self.object.recordings.audio()
        context['video'] = self.object.recordings.video()
        return context

event_detail = EventDetailView.as_view()


class EventMetricsView(HasArtistAssignedMixin, DetailView):
    template_name = 'artist_dashboard/event_metrics.html'
    model = Event

    def get_context_data(self, **kwargs):
        context = super(EventMetricsView, self).get_context_data(**kwargs)
        print dir(self)
        now = timezone.now().date()
        context['weekly_stats'] = context['monthly_stats'] = UserVideoMetric.objects.this_week_counts(
            artist_event_ids=[self.object.id], trends=True, humanize=True)
        context['monthly_stats'] = UserVideoMetric.objects.this_month_counts(
            artist_event_ids=[self.object.id], trends=True, humanize=True)
        context['total_archive_counts'] = UserVideoMetric.objects.total_archive_counts(humanize=True)
        context['event_counts'] = UserVideoMetric.objects.counts_for_event(event_id=self.object.id, humanize=True)
        context['date_counts'] = UserVideoMetric.objects.date_counts(now.month, now.year, [self.object.id])
        return context

event_metrics = EventMetricsView.as_view()


class EventEditView(HasArtistAssignedMixin, event_views.EventEditView):
    form_class = EventEditForm
    template_name = 'artist_dashboard/event_edit.html'

    def get_context_data(self, **kwargs):
        context = super(EventEditView, self).get_context_data(**kwargs)
        context['is_leader'] = self.request.user.artist.is_leader_for_event(self.object)
        context['audio'] = self.object.recordings.audio()
        context['video'] = self.object.recordings.video()
        return context

event_edit = EventEditView.as_view()


class ToggleRecordingStateView(HasArtistAssignedMixin, UpdateView):
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


@login_required
def legal(request):
    user_signed = LegalAgreementAcceptance.objects.filter(user=request.user).exists()
    if not user_signed and 'sign-agreement' in request.POST:
        LegalAgreementAcceptance.objects.create(user=request.user)
        user_signed = True
        messages.success(request, "You've successfully signed the artist agreement.")
    return render(request, 'artist_dashboard/legal.html', {
        'user_signed': user_signed
    })


@login_required
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

    def form_valid(self, form):
        response = super(DashboardLoginView, self).form_valid(form)
        form.user.last_login = timezone.now()
        form.user.save()
        return response

    def get_authenticated_redirect_url(self):
        return reverse('artist_dashboard:home')

login = DashboardLoginView.as_view()


class ForgotPasswordView(allauth_views.PasswordResetView):
    form_class = ArtistResetPasswordForm
    success_url = reverse_lazy("artist_dashboard:forgot_password_done")
    template_name = 'artist_dashboard/forgot_password.html'

forgot_password = ForgotPasswordView.as_view()


class ForgotPasswordDoneView(allauth_views.PasswordResetDoneView):
    template_name = 'artist_dashboard/forgot_password_done.html'

forgot_password_done = ForgotPasswordDoneView.as_view()


class ResetPasswordFromKeyView(allauth_views.PasswordResetFromKeyView):
    template_name = "artist_dashboard/change_password.html"
    success_url = reverse_lazy("artist_dashboard:reset_password_from_key_done")

password_reset_from_key = ResetPasswordFromKeyView.as_view()


class ResetPasswordFromKeyDoneView(allauth_views.PasswordResetFromKeyDoneView):
    template_name = 'artist_dashboard/change_password_done.html'

password_reset_from_key_done = ResetPasswordFromKeyDoneView.as_view()
