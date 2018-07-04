from datetime import timedelta
from cacheops import cached
from django.conf import settings
from django.db.models import Max
from django.template import RequestContext
from django.template.loader import render_to_string
from django_ajax.response import JSONResponse

from events.forms import GigPlayedEditInlineFormset

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from braces.views import SuperuserRequiredMixin
from allauth.account.forms import ChangePasswordForm
import allauth.account.views as allauth_views
from metrics.models import UserVideoMetric
from rest_framework.authtoken.models import Token

from artists.models import Artist, ArtistEarnings, CurrentPayoutPeriod
from events.models import Recording, Event
import events.views as event_views
import users.forms as user_forms
from users.models import LegalAgreementAcceptance
from users.views import HasArtistAssignedMixin, HasArtistAssignedOrIsSuperuserMixin
from .forms import ToggleRecordingStateForm, EventEditForm, ArtistInfoForm,\
    EditProfileForm, ArtistResetPasswordForm, MetricsPayoutForm
from artist_dashboard.tasks import generate_payout_sheet_task, update_current_period_metrics_task


class MyEventsView(HasArtistAssignedMixin, ListView):
    context_object_name = 'gigs'
    paginate_by = 15
    template_name = 'artist_dashboard/my_gigs.html'

    def get_context_data(self, **kwargs):
        context = super(MyEventsView, self).get_context_data(**kwargs)
        paginator = context['paginator']
        current_page_number = context['page_obj'].number
        context.update({
            'total_pages': paginator.num_pages,
            'current_page': current_page_number
        })

        return context

    def get_queryset(self):
        artist = self.request.user.artist

        queryset = artist.gigs_played.select_related('event')
        queryset = self.apply_filters(queryset)
        return queryset

    def apply_filters(self, queryset):
        audio_filter = self.request.GET.get('audio_filter')
        video_filter = self.request.GET.get('video_filter')
        leader_filter = self.request.GET.get('leader_filter')
        order = self.request.GET.get('order')

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

        if order:
            if order == 'newest':
                queryset = queryset.order_by('-event__date')
            elif order == 'oldest':
                queryset = queryset.order_by('event__date')
            else:
                queryset = queryset.order_by('-event__date')

        return queryset


class MyFutureEventsView(MyEventsView):
    def get_queryset(self):
        artist = self.request.user.artist
        now = timezone.now()
        queryset = artist.gigs_played.select_related('event').prefetch_related('event__sets').filter(
            event__start__gte=now
        )

        queryset = self.apply_filters(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(MyFutureEventsView, self).get_context_data(**kwargs)
        context['future_active'] = True
        context['reverse_ajax'] = 'artist_dashboard:my_future_events_ajax'
        return context


my_future_events = MyFutureEventsView.as_view()


class MyEventsAJAXView(MyEventsView):
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data(**kwargs)

        data = {
            'template': render_to_string(
                self.template_name, context,
                context_instance=RequestContext(request)
            ),
            'total_pages': context.get('total_pages'),
            'current_page': context.get('current_page'),
        }

        return JSONResponse(data)


class MyFutureEventsAJAXView(MyEventsAJAXView, MyFutureEventsView):
    reverse_name = 'my_future_events_ajax'
    template_name = 'artist_dashboard/artist-dashboard-events.html'


my_future_events_ajax = MyFutureEventsAJAXView.as_view()


class MyPastEventsView(MyEventsView):
    def get_queryset(self):
        artist = self.request.user.artist
        now = timezone.now()
        queryset = artist.gigs_played.select_related('event').prefetch_related('event__sets').filter(
            event__start__lt=now
        )
        queryset = self.apply_filters(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(MyPastEventsView, self).get_context_data(**kwargs)
        context['past_active'] = True
        context['reverse_ajax'] = 'artist_dashboard:my_past_events_ajax'
        return context


my_past_events = MyPastEventsView.as_view()


class MyPastEventsAJAXView(MyEventsAJAXView, MyPastEventsView):
    reverse_name = 'my_past_events_ajax'
    template_name = 'artist_dashboard/artist-dashboard-events.html'


my_past_events_ajax = MyPastEventsAJAXView.as_view()


class DashboardView(HasArtistAssignedMixin, TemplateView):
    template_name = 'artist_dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        artist = self.request.user.artist
        artist_event_ids = list(self.request.user.artist.event_id_list())

        # need to pass the artist ID to cached function so it caches a different result for each artist
        @cached(timeout=6*60*60)
        def _most_popular_events(artist_id):
            context = {}
            most_popular_event_ids = UserVideoMetric.objects.top_all_time_events(artist_event_ids=artist_event_ids)
            most_popular_events = []
            for event_data in most_popular_event_ids:
                try:
                    event = Event.objects.filter(id=event_data['event_id']).annotate(
                        added=Max('recordings__date_added')).first()
                    most_popular_events.append(event)
                except Event.DoesNotExist:
                    pass
            context['most_popular_events'] = most_popular_events
            return context

        context.update(_most_popular_events(artist.id))
        first_login = self.request.user.is_first_login()
        context['first_login'] = first_login
        context['current_payout_period'] = CurrentPayoutPeriod.objects.first()
        context['previous_payout_period'] = artist.earnings.first()
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
        return context

event_detail = EventDetailView.as_view()


class EventMetricsView(HasArtistAssignedOrIsSuperuserMixin, DetailView):
    template_name = 'artist_dashboard/event_metrics.html'
    model = Event

    def get_context_data(self, **kwargs):
        context = super(EventMetricsView, self).get_context_data(**kwargs)
        now = timezone.now().date()
        context['metrics_server_url'] = settings.METRICS_SERVER_URL
        context['user_token'] = Token.objects.get(user=self.request.user)
        context['weekly_stats'] = context['monthly_stats'] = UserVideoMetric.objects.this_week_counts(
            artist_event_ids=[self.object.id], trends=True, humanize=True)
        context['monthly_stats'] = UserVideoMetric.objects.this_month_counts(
            artist_event_ids=[self.object.id], trends=True, humanize=True)
        context['total_archive_counts'] = UserVideoMetric.objects.total_archive_counts(humanize=True)
        context['event_counts'] = UserVideoMetric.objects.counts_for_event(event_id=self.object.id, humanize=True)
        context['date_counts'] = UserVideoMetric.objects.date_counts(now.month, now.year, [self.object.id])
        context['recordings'] = list(self.object.recordings.select_related('media_file').all().order_by(
            'media_file__media_type', 'set_number'))
        context['recordings'] = [(rec, UserVideoMetric.objects.counts_for_recording(rec.id, trends=True, humanize=True))
                                 for rec in context['recordings']]
        return context

event_metrics = EventMetricsView.as_view()


class EventEditView(HasArtistAssignedMixin, event_views.EventEditView):
    form_class = EventEditForm
    success_url = reverse_lazy("artist_dashboard:my_past_events")
    template_name = 'artist_dashboard/event_edit.html'

    inlines = [GigPlayedEditInlineFormset]
    inlines_names = ['artists']

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


# class MyMetricsView(HasArtistAssignedMixin, TemplateView):
#     template_name = 'artist_dashboard/my_metrics.html'
#
#     def get_context_data(self, **kwargs):
#         context = super(MyMetricsView, self).get_context_data(**kwargs)
#         now = timezone.now().date()
#         context['metrics_server_url'] = settings.METRICS_SERVER_URL
#         context['user_token'] = Token.objects.get(user=self.request.user)
#         artist_event_ids = list(self.request.user.artist.event_id_list())
#         context['artist_event_ids'] = artist_event_ids
#         context['monthly_stats'] = UserVideoMetric.objects.this_month_counts(humanize=True)
#         context['weekly_stats'] = UserVideoMetric.objects.this_week_counts(humanize=True)
#         context['weekly_artist_stats'] = UserVideoMetric.objects.this_week_counts(artist_event_ids=artist_event_ids,
#                                                                                   trends=True, humanize=True)
#         context['monthly_artist_stats'] = UserVideoMetric.objects.this_month_counts(artist_event_ids=artist_event_ids,
#                                                                                     trends=True, humanize=True)
#         context['all_time_for_artist'] = UserVideoMetric.objects.all_time_for_artist(artist_event_ids=artist_event_ids,
#                                                                                      humanize=True)
#         top_weekly_events = UserVideoMetric.objects.top_week_events(artist_event_ids=artist_event_ids, trends=True)
#         context['top_weekly_events'] = self._event_and_counts_from_ids(top_weekly_events)
#         top_all_time_events = UserVideoMetric.objects.top_all_time_events(artist_event_ids=artist_event_ids)
#         context['top_all_time_events'] = self._event_and_counts_from_ids(top_all_time_events)
#         context['date_counts'] = UserVideoMetric.objects.date_counts(now.month, now.year, artist_event_ids)
#         context['archive_date_counts'] = UserVideoMetric.objects.date_counts(now.month, now.year)
#         # last_payment_period = ArtistEarnings.objects.first()
#         # context["new_payment_period_start"] = last_payment_period.period_end + timedelta(days=1)
#         # new_payment_period_end = context["new_payment_period_start"] + timedelta(weeks=12)
#         # context["new_payment_period_end"] = new_payment_period_end.replace(
#         #         day=monthrange(new_payment_period_end.year, new_payment_period_end.month)[1])
#         return context
#
#     def _event_and_counts_from_ids(self, top_events):
#         events = []
#         for event_data in top_events:
#             try:
#                 event = Event.objects.get(id=event_data['event_id'])
#                 counts = UserVideoMetric.objects.counts_for_event(event.id, humanize=True)
#                 counts.update(event_data)
#                 events.append((event, counts))
#             except Event.DoesNotExist:
#                 pass
#         return events
#
# my_metrics = MyMetricsView.as_view()


class AdminMetricsView(SuperuserRequiredMixin, TemplateView):
    template_name = 'artist_dashboard/admin-metrics.html'

    def get_context_data(self, **kwargs):
        context = super(AdminMetricsView, self).get_context_data(**kwargs)
        context['metrics_server_url'] = settings.METRICS_SERVER_URL
        context['user_token'] = Token.objects.get(user=self.request.user)
        now = timezone.now().date()
        context['audio_counts'] = UserVideoMetric.objects.total_archive_counts(trends=True, recording_type='audio',
                                                                               humanize=True)
        context['video_counts'] = UserVideoMetric.objects.total_archive_counts(trends=True, recording_type='video',
                                                                               humanize=True)
        context['date_counts'] = UserVideoMetric.objects.date_counts(now.month, now.year)
        top_weekly_events = UserVideoMetric.objects.top_week_events(trends=True)
        context['top_weekly_events'] = self._event_and_counts_from_ids(top_weekly_events)
        top_all_time_events = UserVideoMetric.objects.top_all_time_events()
        context['top_all_time_events'] = self._event_and_counts_from_ids(top_all_time_events)
        return context

    def _event_and_counts_from_ids(self, top_events):
        events = []
        for event_data in top_events:
            try:
                event = Event.objects.get(id=event_data['event_id'])
                counts = UserVideoMetric.objects.counts_for_event(event.id, humanize=True)
                counts.update(event_data)
                events.append((event, counts))
            except Event.DoesNotExist:
                pass
        return events

admin_metrics = AdminMetricsView.as_view()


class ChangePayoutPeriodView(SuperuserRequiredMixin, UpdateView):
    success_url = reverse_lazy('artist_dashboard:change_payout_period')
    template_name = "artist_dashboard/change_payout_period.html"

    def get_object(self, queryset=None):
        current_period = CurrentPayoutPeriod.objects.first()
        if not current_period:
            start = timezone.now()
            end = start + timedelta(days=90)
            current_period = CurrentPayoutPeriod.objects.create(
                period_start=start,
                period_end=end
            )
        return current_period

    def form_valid(self, form):
        messages.success(self.request, "Payout period dates successfully changed")
        response = super(ChangePayoutPeriodView, self).form_valid(form)
        update_current_period_metrics_task.delay()
        return response

change_payout_period = ChangePayoutPeriodView.as_view()


class PreviousPayoutsView(ListView):
    context_object_name = 'past_payouts'
    template_name = 'artist_dashboard/previous_payouts.html'

    def get_queryset(self):
        return self.request.user.artist.earnings.select_related('payout_period').all()

previous_payouts = PreviousPayoutsView.as_view()


def metrics_payout(request):
    if request.method == 'POST':
        form = MetricsPayoutForm(request.POST)
        if form.is_valid():
            start = form.cleaned_data.get('period_start')
            end = form.cleaned_data.get('period_end')
            revenue = form.cleaned_data.get('revenue')
            operating_cost = form.cleaned_data.get('operating_cost')
            save_earnings = form.cleaned_data.get('save_earnings')
            messages.success(request, "Payout calculation started.")
            generate_payout_sheet_task.delay(start, end, revenue, operating_cost, save_earnings)
        else:
            messages.error(request, "Payout calculation failed. {}".format(form.errors))
        return redirect("artist_dashboard:metrics_payout")
    else:
        form = MetricsPayoutForm()

    return render(request, 'artist_dashboard/metrics_payout.html', {'form': form})


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
