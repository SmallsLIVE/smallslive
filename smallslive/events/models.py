from django.db.models import Count, Max, Q, Sum
from django.utils.text import slugify
from django.utils.timezone import datetime, timedelta, get_default_timezone
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.functional import cached_property
from image_cropping import ImageRatioField
from model_utils import Choices
from model_utils.fields import StatusField
from model_utils.models import QueryManager, TimeStampedModel
from tinymce import models as tinymce_models
from multimedia.s3_storages import ImageS3Storage
from metrics.models import UserVideoMetric


class EventQuerySet(models.QuerySet):
    def upcoming(self):
        return self.filter(start__gte=timezone.now()).order_by('start')

    def past(self):
        return self.filter(start__lt=timezone.now()).order_by('-start')

    def public(self):
        return self.exclude(state=Event.STATUS.Draft).order_by('-start')

    def draft(self):
        return self.filter(state=Event.STATUS.Draft).order_by('-start')

    def most_popular(self):
        return self.exclude(recordings=None).annotate(
            r_play_count=Count('recordings__view_count'), added=Max('recordings__date_added')).order_by('-r_play_count')

    def most_popular_audio(self):
        return self.filter(
            recordings__media_file__media_type='audio').annotate(
            r_play_count=Count('recordings__view_count'), added=Max('recordings__date_added')).order_by('-r_play_count')

    def most_popular_video(self):
        return self.filter(
            recordings__media_file__media_type='video').annotate(
            r_play_count=Count('recordings__view_count'), added=Max('recordings__date_added')).order_by('-r_play_count')

    def most_recent(self):
        return self.exclude(recordings=None).annotate(r_play_count=Count('recordings__view_count'),
                                                      added=Max('recordings__date_added')).order_by('-added')

    def most_recent_audio(self):
        return self.filter(
            recordings__media_file__media_type='audio').annotate(
            r_play_count=Count('recordings__view_count'), added=Max('recordings__date_added')).order_by('-added')

    def most_recent_video(self):
        return self.filter(
            recordings__media_file__media_type='video').annotate(
            r_play_count=Count('recordings__view_count'), added=Max('recordings__date_added')).order_by('-added')

    def last_staff_picks(self):
        return self.filter(
            staff_picked__isnull=False
        ).order_by('-staff_picked__date_picked')
    
    def get_events_by_performers_and_artist(self, number_of_performers_searched, name, just_by_qty):
        #WIP WIPW IPW IPWWIP WPIW 
        if just_by_qty:
            return Event.objects.annotate(num = Count('performers')).filter(Q(num=number_of_performers_searched))

        if len(name.split()) > 1:
            first_name = name.split()[0]
            last_name = name.split()[1]
            return Event.objects.annotate(num = Count('performers')).filter(Q(num=number_of_performers_searched) & Q(
                        performers__first_name__iucontains=first_name) & Q(
                        performers__last_name__iucontains=last_name))
        else:
            return Event.objects.annotate(num = Count('performers')).filter(Q(num=number_of_performers_searched) & Q(
                        performers__first_name__iucontains=name) | Q(
                        performers__last_name__iucontains=name))


    def get_events_by_performers_and_artist(self, number_of_performers_searched, name, just_by_qty):
        #WIP WIPW IPW IPWWIP WPIW 
        if just_by_qty:
            return Event.objects.annotate(num = Count('performers')).filter(Q(num=number_of_performers_searched))

        if len(name.split()) > 1:
            first_name = name.split()[0]
            last_name = name.split()[1]
            return Event.objects.annotate(num = Count('performers')).filter(Q(num=number_of_performers_searched) & Q(
                        performers__first_name__iucontains=first_name) & Q(
                        performers__last_name__iucontains=last_name))
        else:
            return Event.objects.annotate(num = Count('performers')).filter(Q(num=number_of_performers_searched) & Q(
                        performers__first_name__iucontains=name) | Q(
                        performers__last_name__iucontains=name))

            


        #2nd way
        #events_ids = []
        #for event in self:
        #    number_of_performers = len(event.performers.all())
        #    if number_of_performers == number_of_performers_searched:
        #        events_ids.append(event.id)
        
        #temp_sqs = Event.objects.filter(pk__in=events_ids)

        #sqs = []
        #if temp_sqs.count() != 0:
        #    sqs = temp_sqs
        

        
                
    # TODO Select properly
    def event_related_videos(self, event):
        query = self.exclude(state=Event.STATUS.Draft).exclude(
            recordings__isnull=True
        ).exclude(pk=event.pk)

        leader = event.leader
        total_results = 8
        if leader:
            leader_is_leader = (
                Q(artists_gig_info__is_leader=True) &
                Q(artists_gig_info__artist=leader)
            )

            events = list(
                query.filter(
                    leader_is_leader
                ).order_by('-start')[:total_results]
            )
            total_found = len(events)
            if total_found >= total_results:
                return events

            leader_is_performer = (
                Q(artists_gig_info__is_leader=False) &
                Q(artists_gig_info__artist=leader)
            )
            events += list(
                query.filter(
                    leader_is_performer
                ).exclude(
                    pk__in=[event.id for event in events]
                ).order_by('-start')[:(total_results - total_found)]
            )

            total_found = len(events)
            if total_found >= total_results:
                return events

            sideman_is_leader = (
                Q(artists_gig_info__is_leader=True) &
                Q(artists_gig_info__artist__in=event.performers.exclude(
                    pk=leader.pk
                ))
            )
            events += list(
                query.filter(
                    sideman_is_leader
                ).exclude(
                    pk__in=[event.id for event in events]
                ).order_by('-start')[:(total_results - total_found)]
            )

            return events

        return query.order_by('-start')[:total_results]

    def get_today_and_tomorrow_events(self, just_today=False, venue_id=None):
        # All the complexity comes from the events after midnight being
        # considered to be the same before, but internally date is real.

        # cover one day or two
        days = 2
        if just_today:
            days = 1
        date_range_start = get_today_start()
        date_range_end = date_range_start + timedelta(days=days)

        # Initial range. This includes all events from the day
        # even if they have already concluded
        filter_data = {
            'start__gte': date_range_start,
            'end__lte': date_range_end,
        }

        if venue_id:
            filter_data['venue_id'] = venue_id
        qs = self.filter(**filter_data).order_by('start')

        return qs


class CustomImageFieldFile(models.fields.files.ImageFieldFile):

    def get_url(self, bucket_name):
        return self.storage.url(self.name, bucket_name)


class CustomImageField(models.ImageField):

    attr_class = CustomImageFieldFile


class Event(TimeStampedModel):
    SETS = Choices(('22:00-23:00', '10-11pm'), ('23:00-0:00', '11-12pm'), ('0:00-1:00', '12-1am'))
    STATUS = Choices('Published', 'Draft', 'Cancelled')

    title = models.CharField(max_length=500)
    venue = models.ForeignKey('Venue', on_delete=models.CASCADE, blank=True,
                              null=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    set = models.CharField(choices=SETS, blank=True, max_length=10)
    description = tinymce_models.HTMLField(blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    event_type = models.ForeignKey('EventType', blank=True, null=True)
    link = models.CharField(max_length=255, blank=True)
    active = models.BooleanField(default=False)
    date_freeform = models.TextField(blank=True)
    photo = CustomImageField(upload_to='event_images', storage=ImageS3Storage(), max_length=150, blank=True)
    cropping = ImageRatioField('photo', '600x360', help_text="Enable cropping", allow_fullsize=True)
    performers = models.ManyToManyField('artists.Artist', through='GigPlayed', related_name='events')
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    state = StatusField(default=STATUS.Draft)
    slug = models.SlugField(blank=True, max_length=500)
    tickets_url = models.URLField(null=True, blank=True)

    objects = EventQuerySet.as_manager()
    #past = QueryManager(start__lt=datetime.now()).order_by('-start')
    #upcoming = QueryManager(start__gte=datetime.now()).order_by('start')
    date = models.DateField(blank=True, null=True)
    start_streaming_before_minutes = models.IntegerField(default=15)

    # Import information (Mezzrow - possibly other in the future)
    original_id = models.CharField(blank=True, max_length=4096, null=True)
    import_date = models.DateTimeField(blank=True, null=True)

    # Redundant fields from UserVideoMetrics
    # Otherwise it'd be impossible to resolve search queries.
    seconds_played = models.IntegerField(default=0)
    play_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-start']

    def __unicode__(self):
        return u'{} - {}'.format(self.title, self.date)

    def get_date(self):

        start_hour = timezone.localtime(self.start).hour

        if start_hour <= 1:
            return (self.start - timedelta(days=1)).date()

        return self.date

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Event, self).save(force_insert, force_update, using, update_fields)

    def get_actual_start_end(self):
        """ Return real NY time start and end for the event.
        """

        sets = list(self.sets.all())
        sets = sorted(sets, Event.sets_order)

        current_timezone = timezone.get_current_timezone()

        ny_start = datetime.combine(self.date, sets[0].start)
        ny_start = timezone.make_aware(ny_start, timezone=current_timezone)

        ny_end = datetime.combine(self.date, sets[-1].end)
        ny_end = timezone.make_aware(ny_end, timezone=current_timezone)

        return ny_start, ny_end

    def get_set_start(self, set_number):
        sets = list(self.sets.all())
        sets = sorted(sets, Event.sets_order)
        return sets[set_number].start

    def get_play_total(self):
        play_total = 0

        qs = UserVideoMetric.objects.filter(event_id=self.id)
        qs = qs.values('event_id').annotate(play_count=Sum('play_count'))
        if qs.count():
            play_total = qs[0]['play_count']

        return play_total
    
    def get_seconds_total(self):
        seconds_total = 0
        qs = UserVideoMetric.objects.filter(event_id=self.id)
        qs = qs.values('event_id').annotate(seconds_played=Sum('seconds_played'))
        if qs.count():
            seconds_total = qs[0]['seconds_played']

        hours, remainder = divmod(seconds_total, 60 * 60)
        minutes, seconds = divmod(remainder, 60)

        return '{}:{:02d}:{:02d}'.format(hours, minutes, seconds)

    def get_set_hours_display(self):

        time_format = '%-I:%M %p'

        all_sets = self.sets.all()

        if len(all_sets) == 1:
            event_set = all_sets[0]
            return '{} - {}'.format(event_set.start.strftime(time_format),
                                    event_set.end.strftime(time_format))

        sorted_sets = sorted(list(all_sets), Event.sets_order)

        sets_display = ' & '.join(
            [d.start.strftime(time_format) for d in sorted_sets])

        return sets_display

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'pk': self.id, 'slug': slugify(self.title)})

    def full_title(self):
        return u"{0} {1}".format(self.title, self.subtitle)

    def get_photo_url(self):
        """Mezzrow has different buckets. S3 storage is overriden and bucket name has to be passed"""
        # TODO: store bucket name in Venue
        if self.venue and self.venue.name == 'Mezzrow':
            bucket_name = 'mezzrowmedia'
        else:
            bucket_name = 'smallslivestatic'

        return self.photo.get_url(bucket_name)

    def performers_string(self, separator=", "):
        "Returns the comma-separated list of performers (including the leader) as a string"
        return self.leader_string() + separator + self.sidemen_string()

    def performers_with_instruments_string(self, separator=", "):
        "Returns the comma-separated list of performers with instruments (including the leader) as a string"
        return self.leader_with_instrument_string() + separator + self.sidemen_with_instruments_string()

    def sidemen_string(self, separator=", "):
        "Returns the comma-separated list of sidemen (without the leader) as a string"
        performers = self.artists_gig_info.filter(is_leader=False).order_by('sort_order').select_related(
            'artist').values_list('artist__first_name', 'artist__last_name')
        # Make full names
        performers = [u"{0} {1}".format(first, last) for first, last in performers]
        return separator.join(performers)

    def sidemen_with_instruments_string(self, separator=", "):
        """
        Returns the comma-separated list of sidemen with instrument abbreviations
        (without the leader) as a string
        """
        performers = self.artists_gig_info.filter(is_leader=False).order_by('sort_order').select_related(
            'artist', 'role').values_list('artist__first_name', 'artist__last_name', 'role__name')
        # Make full names
        performers = [u"{0} {1} ({2})".format(first, last, instrument) for first, last, instrument in performers]
        return separator.join(performers)

    def leader_string(self):
        leader = self.artists_gig_info.filter(is_leader=True).first()
        if leader:
            text = leader.artist.full_name()
        else:
            text = u""
        return text

    def leader_with_instrument_string(self):
        leader = self.artists_gig_info.select_related('artist', 'role').filter(is_leader=True).first()
        if leader:
            text = u"{0} ({1})".format(leader.artist.full_name(), leader.role.name)
        else:
            text = u""
        return text

    def display_title(self):
        """
        Returns the event display title. If the title is defined, returns the title, otherwise it generates
        one from the performer names and their roles.
        """
        leader = self.leader_string()
        if self.title:
            display_title = self.title + " w/ " + self.performers_string()
        elif leader:
            display_title = leader + " w/ " + self.sidemen_string()
        else:
            display_title = self.sidemen_string()
        return display_title

    def display_title_with_instruments(self):
        """
        Returns the event display title. If the title is defined, returns the title, otherwise it generates
        one from the performer names and their roles.
        """
        leader = self.leader_with_instrument_string()
        if self.title:
            display_title = self.title + " w/ " + self.performers_with_instruments_string()
        elif leader:
            display_title = leader + " w/ " + self.sidemen_with_instruments_string()
        else:
            display_title = self.sidemen_with_instruments_string()
        return display_title

    @staticmethod
    def sets_order(set1, set2):

        if set1.start.hour <= 5 and set2.start.hour <= 5 or \
                set1.start.hour > 5 and set2.start.hour > 5:
            if set1.start < set2.start:
                return -1
            elif set1.start > set2.start:
                return 1
            else:
                return 0
        elif set1.start.hour <= 5:  # and set2.start.hour > 5
            return 1
        elif set2.start.hour <= 5:  # and set1.start.hour > 5
            return -1

    @staticmethod
    def events_order(event1, event2):
        if event1.date < event2.date:
            return -1
        elif event1.date > event2.date:
            return 1
        else:
            sets1 = list(event1.sets.all())
            sets1 = sorted(sets1, Event.sets_order)
            start1 = sets1[0].start
            sets2 = list(event2.sets.all())
            sets2 = sorted(sets2, Event.sets_order)
            start2 = sets2[0].start
            if start1.hour <= 5 and start2.hour <= 5 or start1.hour >= 5 and start2.hour >= 5:
                if start1.hour < start2.hour:
                    return -1
                elif start1.hour > start2.hour:
                    return 1
                else:  # same hour
                    if start1.minute <= start2.minute:
                        return -1
                    else:
                        return 1
            else:
                if start1.hour <= 5:
                    return 1
                else:
                    return -1

    def get_range(self):
        sets = list(self.sets.all())
        sets = sorted(sets, Event.sets_order)
        start = sets[0].start
        end = sets[-1].end

        return start, end

    @property
    def is_past(self):
        """
        Checks if the event happened in the past and already ended.
        """
        local_datetime = timezone.localtime(timezone.now())
        local_date = local_datetime.date()
        local_time = local_datetime.time()

        start, end = self.get_range()

        if self.date < local_date - timedelta(days=1):
            return True
        if self.date < local_date and end.hour > 5:
            return True
        elif self.date == local_date - timedelta(days=1) and end.hour <= 5:
            return end < local_time
        elif self.date == local_date:
            return end < local_time and end.hour > 5

    @property
    def is_future(self):
        """
        Checks if the event will happen in the future and hasn't yet started.
        """
        local_datetime = timezone.localtime(timezone.now())
        local_date = local_datetime.date()
        local_time = local_datetime.time()

        start, end = self.get_range()

        # After midnight events always have the previous date
        if local_time.hour <= 5:
            local_date -= timedelta(days=1)

        match_date = local_date <= self.date
        time_before_start = local_date < self.date or \
                            local_time < start or \
                            local_time.hour < 5 < start.hour

        return match_date and time_before_start

    def is_live_or_about_to_begin(self, about_to_begin=False):
        """
        An event is live depending on start and end time.
        'about_to_begin' considers the actual start date minus X minutes (typically 15) set
        in the database as 'start_streaming_before_minutes'
        """
        local_datetime = timezone.localtime(timezone.now())
        local_date = local_datetime.date()
        local_time = local_datetime.time()

        start, end = self.get_range()

        if about_to_begin:
            # convert to datetime temporarily to subtract minutes
            start = datetime.combine(local_date, start)
            start = timezone.make_aware(start, timezone=(timezone.get_current_timezone()))
            start = start - timedelta(
                minutes=self.start_streaming_before_minutes)
            start = start.time()

        # After midnight events always have the previous date
        if local_time.hour <= 5:
            local_date -= timedelta(days=1)

        # Start - End examples:
        # 19:30 - 22:30
        # 23:00 - 1:00
        # 1:00 - 4:00
        # local time can be in between of any of those
        # 1. date has  to match
        # start <= current time <= end if both start and end <= 5 or > 5
        # if start = 22:30 <= current time <= end = 2:00, that's the 'difficult' case.
        # current time can be before of after midnight.

        match_date = local_date == self.date
        time_after_start_and_before_end = start <= local_time <= end and \
                                          end.hour > start.hour > 5
        start_before_midnight_and_end_after = (start <= local_time or
                                               local_time <= end) \
                                               and end.hour <= 5 < start.hour

        return match_date and \
               (time_after_start_and_before_end or
                start_before_midnight_and_end_after)

    @property
    def show_streaming(self):
        return self.is_live_or_about_to_begin(about_to_begin=True)

    @property
    def is_live(self):
        return self.is_live_or_about_to_begin(about_to_begin=False)

    def get_live_set(self):
        sets = list(self.sets.all())
        sets = sorted(sets, Event.sets_order)

        local_datetime = timezone.localtime(timezone.now())
        local_date = local_datetime.date()
        local_time = local_datetime.time()

        live_set = None
        for item in sets:
            if local_date == self.date:
                if item.start < local_time < item.end:
                    live_set = item
                    break
                if item.end < item.start < local_time:
                    live_set = item
                    break

        return live_set

    def get_live_stream(self):

        # TODO: set live stream url in model field

        url = ''

        if self.venue.name == 'Mezzrow':
            url = 'https://www.ustream.tv/embed/23240580?html5ui'
        elif self.venue.name == 'Smalls':
            url = 'https://www.ustream.tv/embed/23240575?html5ui'

        return url

    def get_next_event(self):
        next_events = list(Event.objects.get_today_and_tomorrow_events(
            venue_id=self.venue_id))

        next_event = None
        while next_events and not next_event:
            item = next_events.pop(0)
            if self.pk == item.pk:
                next_event = item

        next_event = next_events.pop(0) if next_events else None

        return next_event

    @property
    def is_today(self):
        day_start = get_today_start()
        day_end = day_start + timedelta(days=1)

        return day_start.date() <= self.date < day_end.date()

    def get_performers(self):
        return self.artists_gig_info.select_related('artist', 'role')

    @property
    def leader(self):
        try:
            gig_info = self.artists_gig_info.filter(is_leader=True).first()
            leader = gig_info.artist
        except (GigPlayed.DoesNotExist, AttributeError):
            leader = None
        return leader

    def listing_date(self):
        """
        Shows the listing date for an event, for instance an event that is technically
        on 3/12 at 1:00 AM has a listing date of 3/11 to be correctly grouped with other
        events under that date.
        """
        local_time = timezone.localtime(self.start)
        date = local_time.date()
        if 0 <= local_time.hour <= 4:
            date += timedelta(days=-1)

        return date

    def is_early_morning(self):
        """
        Shows the listing date for an event, for instance an event that is technically
        on 3/12 at 1:00 AM has a listing date of 3/11 to be correctly grouped with other
        events under that date.
        """
        date = self.start.date()
        listing_date = self.listing_date()
        return date != listing_date

    def status_css_class(self):
        """
        Returns the Bootstrap label CSS class for the event status (published/draft/cancelled/hidden)
        """
        CSS_STATES = {
            'Published': 'label-success',
            'Draft': 'label-warning',
            'Cancelled': 'label-danger',
        }
        return CSS_STATES[self.state]

    def is_cancelled(self):
        return self.state == self.STATUS.Cancelled

    def autocomplete_label(self):
        return self.title

    def autocomplete_sublabel(self):
        return u"{dt.month}/{dt.day}/{dt.year}".format(dt=self.start)

    def has_started(self):
        return timezone.now() > self.start

    @cached_property
    def audio_status(self):
        audio_count = self.recordings.all().audio().count()
        if audio_count == 0:
            status = "none"
        else:
            audio_published_count = self.recordings.all().audio().published().count()
            if audio_published_count == 0:
                status = "blocked"
            elif audio_published_count < audio_count:
                status = "partial"
            else:
                status = "published"
        return status

    @cached_property
    def published_videos(self):
        return self.recordings.all().video().published()

    @cached_property
    def video_status(self):
        video_count = self.recordings.all().video().count()
        if video_count == 0:
            status = "none"
        else:
            video_published_count = self.recordings.all().video().published().count()
            if video_published_count == 0:
                status = "blocked"
            elif video_published_count < video_count:
                status = "partial"
            else:
                status = "published"
        return status

    @cached_property
    def published_audio(self):
        return self.recordings.all().audio().published()

    @cached_property
    def photo_crop_box(self):
        if not self.cropping or '-' in self.cropping:
            return
        top_x, top_y, bottom_x, bottom_y = self.cropping.split(',')
        return ((top_x, top_y), (bottom_x, bottom_y))

    def get_sets_info_dict(self):
        sets_info = []
        for item in sorted(list(self.sets.all()), Event.sets_order):
            sets_info.append({'start': item.start})

        return sets_info

    def get_artists_info_dict(self):
        # DOCUMENT: Why is this necessary.
        event_artists_info = []
        for gig in self.artists_gig_info.select_related('artist', 'role'):
            event_artists_info.append({
                'name': gig.artist.full_name(),
                'role': gig.role.name,
                'absolute_url': gig.artist.get_absolute_url()})
        return event_artists_info

    def get_tickets(self):
        tickets = []
        for event_set in self.sets.all():
            tickets += list(event_set.tickets.all())

        return tickets


class RecordingQuerySet(models.QuerySet):
    def video(self):
        return self.filter(media_file__media_type='video')

    def audio(self):
        return self.filter(media_file__media_type='audio')

    def published(self):
        return self.filter(state=Recording.STATUS.Published)

    def hidden(self):
        return self.filter(state=Recording.STATUS.Hidden)

    def most_popular(self):
        return self.order_by('-view_count')

    def most_recent(self):
        return self.order_by('-date_added')


class RecordingManager(models.Manager.from_queryset(RecordingQuerySet)):
    use_for_related_fields = True


class Recording(models.Model):
    STATUS = Choices('Published', 'Hidden')
    FILTER_STATUS = STATUS + ['None']

    media_file = models.OneToOneField('multimedia.MediaFile', related_name='recording')
    event = models.ForeignKey(Event, related_name='recordings')
    title = models.CharField(max_length=150, blank=True)
    set_number = models.IntegerField(default=1)
    state = StatusField(default=STATUS.Published)
    date_added = models.DateTimeField(auto_now_add=True)
    view_count = models.PositiveIntegerField(default=0)

    objects = RecordingManager()

    class Meta:
        ordering = ['set_number']

    def __unicode__(self):
        return u'State: {}, Event: {}, Set: {}'.format(
            repr(self.state) or u'N/A',
            self.event or u'N/A',
            self.set_number or u'N/A',
        )

    def is_published(self):
        return self.state == self.STATUS.Published

    def is_valid_status(self, status):
        return status in self.STATUS or status == "None"

    def get_redirect_url(self):
        """
        Redirect view used to track media using jwplayer analytics in a way that they have a
        consistent URL and not have the S3 access key.
        """
        return reverse('media_redirect', kwargs={'recording_id': self.id})


class EventType(models.Model):
    name = models.CharField(max_length=50)
    parent = models.IntegerField()

    def __unicode__(self):
        return self.name


class EventSet(models.Model):
    start = models.TimeField()
    end = models.TimeField(blank=True, null=True)
    event = models.ForeignKey('events.Event', related_name='sets')
    video_recording = models.OneToOneField('events.Recording', related_name='set_is_video', blank=True, null=True)
    audio_recording = models.OneToOneField('events.Recording', related_name='set_is_audio', blank=True, null=True)

    def __unicode__(self):
        return '{} - {}'.format(self.start, self.end)

    def save(self, *args, **kwargs):
        obj = super(EventSet, self).save(*args, **kwargs)

        # Keep actual start, end dates of the event.
        (self.event.start, self.event.end) = self.event.get_actual_start_end()
        self.event.save()

        return obj

    @property
    def has_media(self):
        return self.video_recording or self.audio_recording

    @property
    def utc_start(self):
        real_date = self.event.date
        if 0 <= self.start.hour < 5:
            real_date = real_date + timedelta(days=1)

        ny_start = datetime.combine(real_date, self.start)
        return timezone.make_aware(ny_start, timezone=(timezone.get_current_timezone()))

    @property
    def utc_end(self):
        ny_end = datetime.combine(self.event.date, self.end)
        return timezone.make_aware(ny_end, timezone=(timezone.get_current_timezone()))


class GigPlayedQuerySet(models.QuerySet):
    def upcoming(self):
        return self.filter(event__start__gte=timezone.now()).order_by('-event__start')

    def past(self):
        return self.filter(event__start__lt=timezone.now()).order_by('event__start')


class GigPlayed(models.Model):
    artist = models.ForeignKey('artists.Artist', related_name='gigs_played')
    event = models.ForeignKey('events.Event', related_name='artists_gig_info')
    role = models.ForeignKey('artists.Instrument')
    is_leader = models.BooleanField(default=False)
    sort_order = models.CharField(max_length=30, blank=True)
    is_admin = models.BooleanField(default=False)

    objects = GigPlayedQuerySet.as_manager()

    class Meta:
        ordering = ['event', 'sort_order', 'is_leader']


class Venue(models.Model):

    name = models.CharField(max_length=100, unique=True)
    audio_bucket_name = models.CharField(max_length=4096, default='smallslivemp3')
    video_bucket_name = models.CharField(max_length=4096, default='smallslivevid')

    def __unicode__(self):
        return self.name
    
    @property
    def short_name(self):
        return self.name.split(' ')[0]

    @property
    def color(self):
        # TODO: un-hardcode o_o'
        if 'mezzrow' in self.name.lower():
            return 'rgb(241, 187, 83)'
        return '#D21535'


class ShowDefaultTime(models.Model):
    venue = models.ForeignKey('Venue', on_delete=models.CASCADE, blank=False)
    first_set = models.TimeField(blank=False)
    second_set = models.TimeField(blank=False)
    set_duration = models.IntegerField(default=1)
    title = models.CharField(max_length=100, default='Set duration')

    def sets_start(self):
        return self.first_set.strftime('%H:%M') + "-" + self.second_set.strftime('%H:%M') 

    def sets_readable_start(self):
        return self.first_set.strftime('%I:%M %p') + " - " + self.second_set.strftime('%I:%M %p') 

    def __unicode__(self):
        return self.sets_readable_start() + "    " + self.venue.name


class StaffPick(models.Model):
    event = models.OneToOneField('events.Event', related_name='staff_picked')
    date_picked = models.DateTimeField()


def get_today_start():
    """ Day actually starts at 6 am"""

    start = timezone.localtime(timezone.now())
    start = start.replace(hour=6, minute=0)

    return start


class Comment(models.Model):

    STATUS_APPROVED = 'A'
    STATUS_REJECTED = 'R'
    STATUS_IN_REVIEW = 'IR'

    STATUS = (
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_IN_REVIEW, 'In Review'),
    )

    status = models.CharField(choices=STATUS, default=STATUS_APPROVED,
                              max_length=2)
    event_set = models.ForeignKey(EventSet, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='comments')
    created_at = models.DateTimeField()
    content = models.TextField(max_length=500, null=True, blank=False)

    def save(self, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        super(Comment, self).save(**kwargs)
