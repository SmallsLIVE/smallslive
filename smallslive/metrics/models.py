import calendar
import datetime
import itertools
import random

from django.db import models
from django.db.models import Sum
from django.utils import timezone

from .utils import format_timespan

RANGE_YEAR = 'year'
RANGE_MONTH = 'month'
RANGE_WEEK = 'week'


class MetricsQuerySet(models.QuerySet):
    def audio(self):
        return self.filter(recording_type='A')

    def video(self):
        return self.filter(recording_type='V')

    def video_counts(self):
        counts = self.filter(recording_type='V').aggregate(seconds_played=Sum('seconds_played'), play_count=Sum('play_count'))
        counts['seconds_played'] = counts['seconds_played'] or 0
        counts['play_count'] = counts['play_count'] or 0
        return counts

    def audio_counts(self):
        counts = self.filter(recording_type='A').aggregate(seconds_played=Sum('seconds_played'), play_count=Sum('play_count'))
        counts['seconds_played'] = counts['seconds_played'] or 0
        counts['play_count'] = counts['play_count'] or 0
        return counts

    def total_counts(self):
        counts = self.aggregate(seconds_played=Sum('seconds_played'), play_count=Sum('play_count'))
        counts['seconds_played'] = counts['seconds_played'] or 0
        counts['play_count'] = counts['play_count'] or 0
        return counts

    def total_counts_annotate(self):
        return self.annotate(seconds_played=Sum('seconds_played'), play_count=Sum('play_count'))

    def most_popular_audio(self, weekly=False, range_size=None):
        return self.audio().most_popular(weekly=weekly, range_size=range_size)

    def most_popular_video(self, weekly=False, range_size=None):
        return self.video().most_popular(weekly=weekly, range_size=range_size)

    def most_popular(self, weekly=False, range_size=None):
        qs = self

        range_start = None
        range_end = None
        if range_size:
            if range_size == RANGE_WEEK:
                range_end, range_start = self.get_weekly_range()
            elif range_size == RANGE_MONTH:
                range_end, range_start = self.get_monthly_range()
            elif range_size == RANGE_YEAR:
                range_end, range_start = self.get_year_range()

        else:
            if weekly:
                range_end, range_start = self.get_weekly_range()

        if range_start and range_end:
            qs = qs.filter(date__range=(range_start, range_end))

        return qs.values('event_id').annotate(
            count=Sum('seconds_played')
        ).order_by('-count')

    def get_weekly_range(self):
        now = timezone.now()
        range_start = (now - datetime.timedelta(days=now.weekday())).date()
        range_end = range_start + datetime.timedelta(weeks=1)
        return range_end, range_start

    def get_monthly_range(self):
        now = timezone.now()
        current_year = now.year
        current_month = now.month

        range_start = datetime.date(current_year, current_month, 1)
        range_end = datetime.date(
            current_year, current_month, calendar.monthrange(
                current_year, current_month
            )[1]
        )

        return range_end, range_start

    def get_year_range(self):
        now = timezone.now()
        current_year = now.year

        range_start = datetime.date(current_year, 1, 1)
        range_end = datetime.date(current_year, 12, 31)

        return range_end, range_start


class MetricsManager(models.Manager):
    def get_queryset(self):
        return MetricsQuerySet(self.model, using=self._db)

    def counts_for_artist(self, artist_recording_ids, humanize=False):
        counts = self.get_queryset().filter(recording_id__in=artist_recording_ids).total_counts()
        if humanize:
            counts['time_played'] = format_timespan(counts['seconds_played'])
        return counts

    def seconds_played_for_all_events(self, start_date, end_date):
        qs = self.get_queryset().filter(date__range=(start_date, end_date)).values(
            'event_id').annotate(seconds_played=Sum('seconds_played'))
        return qs

    def _calculate_percentage(self, event_stat, total_stat):
        if total_stat > 0:
            percentage = float(event_stat) / float(total_stat)
            percentage *= 100
        else:
            percentage = None
        return percentage

    def _calculate_week_trends(self, counts, week_start, week_end, recording_type=None, event_ids=None, recording_id=None):
        last_week_start = week_start - datetime.timedelta(weeks=1)
        last_week_end = week_end - datetime.timedelta(weeks=1)
        qs = self.get_queryset().filter(date__range=(last_week_start, last_week_end))
        if event_ids:
            if len(event_ids) > 1:
                qs = qs.filter(event_id__in=event_ids)
            else:
                qs = qs.filter(event_id=event_ids[0])
        elif recording_id:
            qs = qs.filter(recording_id=recording_id)

        if recording_type == "audio":
            last_week_counts = qs.audio_counts()
        elif recording_type == "video":
            last_week_counts = qs.video_counts()
        else:
            last_week_counts = qs.total_counts()
        this_week_seconds = int(counts['seconds_played'])
        last_week_seconds = int(last_week_counts['seconds_played'])
        if last_week_seconds != 0:
            counts['seconds_played_trend'] = ((this_week_seconds - last_week_seconds) / float(last_week_seconds)) * 100
        else:
            counts['seconds_played_trend'] = None

        this_week_plays = counts['play_count']
        last_week_plays = last_week_counts['play_count']
        if last_week_plays != 0:
            counts['play_count_trend'] = ((this_week_plays - last_week_plays) / float(last_week_plays)) * 100
        else:
            counts['play_count_trend'] = None
        return counts

    def _calculate_month_trends(self, counts, month, year, recording_type=None, event_ids=None, recording_id=None):
        this_month = datetime.date(year, month, 1)
        last_month = this_month - datetime.timedelta(days=1)
        qs = self.get_queryset().filter(date__month=last_month.month, date__year=last_month.year)
        if event_ids:
            if len(event_ids) > 1:
                qs = qs.filter(event_id__in=event_ids)
            else:
                qs = qs.filter(event_id=event_ids[0])
        elif recording_id:
            qs = qs.filter(recording_id=recording_id)
            
        if recording_type == "audio":
            last_month_counts = qs.audio_counts()
        elif recording_type == "video":
            last_month_counts = qs.video_counts()
        else:
            last_month_counts = qs.total_counts()
        this_month_seconds = counts['seconds_played']
        last_month_seconds = last_month_counts['seconds_played']
        if last_month_seconds != 0:
            counts['seconds_played_trend'] = ((this_month_seconds - last_month_seconds) / float(last_month_seconds)) * 100
        else:
            counts['seconds_played_trend'] = None

        this_month_plays = counts['play_count']
        last_month_plays = last_month_counts['play_count']
        if last_month_plays != 0:
            counts['play_count_trend'] = ((this_month_plays - last_month_plays) / float(last_month_plays)) * 100
        else:
            counts['play_count_trend'] = None
        return counts

    def counts_for_event(self, event_id, humanize=False):
        now = timezone.now()
        week_start = (now - datetime.timedelta(days=now.weekday())).date()
        week_end = week_start + datetime.timedelta(weeks=1)
        this_week_counts = self.get_queryset().filter(
            date__range=(week_start, week_end), event_id=event_id).total_counts()
        this_month_counts = self.get_queryset().filter(
            date__month=now.month, date__year=now.year, event_id=event_id).total_counts()
        all_time_counts = self.get_queryset().filter(event_id=event_id).total_counts()

        total_archive_counts = self.total_archive_counts()
        this_week_counts['play_count_percentage'] = self._calculate_percentage(this_week_counts['play_count'],
                                                                               total_archive_counts['week'][
                                                                                   'play_count'])
        this_week_counts['seconds_played_percentage'] = self._calculate_percentage(this_week_counts['seconds_played'],
                                                                                   total_archive_counts['week'][
                                                                                       'seconds_played'])
        this_month_counts['play_count_percentage'] = self._calculate_percentage(this_month_counts['play_count'],
                                                                                total_archive_counts['month'][
                                                                                    'play_count'])
        this_month_counts['seconds_played_percentage'] = self._calculate_percentage(this_month_counts['seconds_played'],
                                                                                    total_archive_counts['month'][
                                                                                        'seconds_played'])
        all_time_counts['play_count_percentage'] = self._calculate_percentage(all_time_counts['play_count'],
                                                                              total_archive_counts['all_time'][
                                                                                  'play_count'])
        all_time_counts['seconds_played_percentage'] = self._calculate_percentage(all_time_counts['seconds_played'],
                                                                                  total_archive_counts['all_time'][
                                                                                      'seconds_played'])

        if humanize:
            this_week_counts['time_played'] = format_timespan(this_week_counts['seconds_played'])
            this_month_counts['time_played'] = format_timespan(this_month_counts['seconds_played'])
            all_time_counts['time_played'] = format_timespan(all_time_counts['seconds_played'])
        counts = {
            'week': this_week_counts,
            'month': this_month_counts,
            'all_time': all_time_counts
        }
        return counts

    def all_time_for_artist(self, artist_event_ids, humanize=False):
        all_time_counts = self.get_queryset().filter(event_id__in=artist_event_ids).total_counts()
        total_archive_counts = self.total_archive_counts()
        all_time_counts['play_count_percentage'] = self._calculate_percentage(all_time_counts['play_count'],
                                                                              total_archive_counts['all_time'][
                                                                                  'play_count'])
        all_time_counts['seconds_played_percentage'] = self._calculate_percentage(all_time_counts['seconds_played'],
                                                                                  total_archive_counts['all_time'][
                                                                                      'seconds_played'])
        if humanize:
            all_time_counts['time_played'] = format_timespan(all_time_counts['seconds_played'])

        return all_time_counts

    def counts_for_recording(self, recording_id, trends=False, humanize=False):
        now = timezone.now()
        week_start = (now - datetime.timedelta(days=now.weekday())).date()
        week_end = week_start + datetime.timedelta(weeks=1)
        this_week_counts = self.get_queryset().filter(
            date__range=(week_start, week_end), recording_id=recording_id).total_counts()

        if trends:
            this_week_counts = self._calculate_week_trends(this_week_counts, week_start, week_end, recording_id=recording_id)

        all_time_counts = self.get_queryset().filter(recording_id=recording_id).total_counts()

        if humanize:
            this_week_counts['time_played'] = format_timespan(this_week_counts['seconds_played'])
            all_time_counts['time_played'] = format_timespan(all_time_counts['seconds_played'])
        counts = {
            'week': this_week_counts,
            'all_time': all_time_counts
        }
        return counts

    def total_archive_counts(self, trends=False, recording_type=None, humanize=False):
        now = timezone.now()
        week_start = (now - datetime.timedelta(days=6)).date()
        week_end = now
        this_week_qs = self.get_queryset().filter(date__range=(week_start, week_end))
        this_month_qs = self.get_queryset().filter(date__month=now.month, date__year=now.year)
        all_time_qs = self.get_queryset()

        if recording_type == 'audio':
            this_week_counts = this_week_qs.audio_counts()
            this_month_counts = this_month_qs.audio_counts()
            all_time_counts = all_time_qs.audio_counts()
        elif recording_type == 'video':
            this_week_counts = this_week_qs.video_counts()
            this_month_counts = this_month_qs.video_counts()
            all_time_counts = all_time_qs.video_counts()
        else:
            this_week_counts = this_week_qs.total_counts()
            this_month_counts = this_month_qs.total_counts()
            all_time_counts = all_time_qs.total_counts()

        if trends:
            this_week_counts = self._calculate_week_trends(this_week_counts, week_start, week_end, recording_type=recording_type)
            this_month_counts = self._calculate_month_trends(this_month_counts, now.month, now.year, recording_type=recording_type)

        if humanize:
            this_week_counts['time_played'] = format_timespan(this_week_counts['seconds_played'])
            this_month_counts['time_played'] = format_timespan(this_month_counts['seconds_played'])
            all_time_counts['time_played'] = format_timespan(all_time_counts['seconds_played'])
        counts = {
            'week': this_week_counts,
            'month': this_month_counts,
            'all_time': all_time_counts
        }
        return counts

    def this_month_total_archive(self, humanize=False):
        now = timezone.now().date()
        counts = self.get_queryset().filter(date__month=now.month, date__year=now.year).total_counts()
        if humanize:
            counts['time_played'] = format_timespan(counts['seconds_played'])
        return

    def this_week_counts(self, artist_event_ids=None, trends=False, humanize=False):
        now = timezone.now()
        week_start = (now - datetime.timedelta(days=now.weekday())).date()
        week_end = week_start + datetime.timedelta(weeks=1)
        qs = self.get_queryset().filter(date__range=(week_start, week_end))
        # needed because sometimes an empty list is passed
        if artist_event_ids is not None:
            counts = qs.filter(event_id__in=artist_event_ids).total_counts()
            if trends:
                counts = self._calculate_week_trends(counts, week_start, week_end, event_ids=artist_event_ids)
        else:
            counts = qs.total_counts()
        if humanize:
            counts['time_played'] = format_timespan(counts['seconds_played'])
        return counts

    def monthly_counts(self, month, year, artist_event_ids=None, trends=False, humanize=False):
        qs = self.get_queryset().filter(date__month=month, date__year=year)
        # needed because sometimes an empty list is passed
        if artist_event_ids is not None:
            counts = qs.filter(event_id__in=artist_event_ids).total_counts()
            if trends:
                counts = self._calculate_month_trends(counts, month, year, event_ids=artist_event_ids)
        else:
            counts = qs.total_counts()
        if humanize:
            counts['time_played'] = format_timespan(counts['seconds_played'] or 0)
        return counts

    def this_month_counts(self, artist_event_ids=None, trends=False, humanize=False):
        now = timezone.now()
        return self.monthly_counts(now.month, now.year, artist_event_ids=artist_event_ids,
                                   trends=trends, humanize=humanize)

    def this_month_counts_for_artist(self, artist_event_ids, trends=False, humanize=False):
        now = timezone.now()
        return self.monthly_counts(now.month, now.year, artist_event_ids=artist_event_ids,
                                   trends=trends, humanize=humanize)

    def date_counts(self, month, year, artist_event_ids=None):
        """
        Returns a list of play counts and seconds played per day. If the requested month is the current
        month, return values only up to the current day (don't add zeroes for remaining months)
        """
        qs = self.get_queryset().filter(date__month=month, date__year=year)
        if artist_event_ids:
            if len(artist_event_ids) == 1:
                qs = qs.filter(event_id=artist_event_ids[0])
            else:
                qs = qs.filter(event_id__in=artist_event_ids)

        qs = qs.values('date', 'recording_type').order_by('date').total_counts_annotate()

        now = timezone.now().date()
        if now.month == month and now.year == year:
            days_in_month = now.day
        else:
            days_in_month = calendar.monthrange(year, month)[1]
        days = range(1, days_in_month+1)
        audio_play_counts = {}
        audio_minutes_counts = {}
        video_play_counts = {}
        video_minutes_counts = {}
        for entry in qs:
            day = entry['date'].day
            if entry['recording_type'] == 'V':
                video_play_counts[day] = entry['play_count']
                video_minutes_counts[day] = entry['seconds_played'] / 60
            else:
                audio_play_counts[day] = entry['play_count']
                audio_minutes_counts[day] = entry['seconds_played'] / 60
        counts = {}
        counts['audio_plays_list'] = [audio_play_counts.get(day_number, 0) for day_number in days]
        counts['audio_minutes_list'] = [audio_minutes_counts.get(day_number, 0) for day_number in days]
        counts['video_plays_list'] = [video_play_counts.get(day_number, 0) for day_number in days]
        counts['video_minutes_list'] = [video_minutes_counts.get(day_number, 0) for day_number in days]
        counts['total_plays_list'] = [a+v for a, v in zip(counts['audio_plays_list'], counts['video_plays_list'])]
        counts['total_minutes_list'] = [a+v for a, v in zip(counts['audio_minutes_list'], counts['video_minutes_list'])]
        counts['dates'] = ["{0}/{1}".format(month, day) for day in days]
        return counts

    def top_week_events(self, artist_event_ids=None, trends=False):
        now = timezone.now()
        week_start = (now - datetime.timedelta(days=now.weekday())).date()
        week_end = week_start + datetime.timedelta(weeks=1)
        qs = self.get_queryset().filter(date__range=(week_start, week_end))
        if artist_event_ids:
            qs = qs.filter(event_id__in=artist_event_ids)
        counts = list(qs.values('event_id').total_counts_annotate().order_by('-seconds_played')[:10])
        if trends:
            for idx, count in enumerate(counts):
                counts[idx] = self._calculate_week_trends(count, week_start, week_end, event_ids=[count['event_id']])
        return counts

    def top_all_time_events(self, artist_event_ids=None):
        qs = self.get_queryset()
        if artist_event_ids:
            qs = qs.filter(event_id__in=artist_event_ids)
        return qs.values('event_id').total_counts_annotate().order_by('-seconds_played')[:10]

    def create_random(self):
        today = timezone.now().date()
        params = {}
        params['date'] = today - datetime.timedelta(days=random.randrange(1, 90))
        params['recording_id'] = random.randrange(1, 10)
        params['user_id'] = random.randrange(1, 10)
        params['seconds_played'] = random.randrange(10, 600, 10)
        self.create(**params)

    def create_random_for_user(self, user_id):
        today = timezone.now()
        params = {}
        recordings = [
            # Spike's recordings
            {'id': 13326, 'recording_type': 'V', 'event_id': 9594},
            {'id': 13396, 'recording_type': 'A', 'event_id': 9594},
            {'id': 18093, 'recording_type': 'V', 'event_id': 10061},
            {'id': 17731, 'recording_type': 'A', 'event_id': 9849},
            # Carlos Abadie's recordings
            {'id': 966, 'recording_type': 'A', 'event_id': 5568},
            {'id': 1037, 'recording_type': 'A', 'event_id': 5478},
            {'id': 16962, 'recording_type': 'V', 'event_id': 9670},
        ]
        recordings_iter = itertools.cycle(recordings)
        params['user_id'] = user_id
        for day in range(1, 90):
            params['date'] = (today - datetime.timedelta(days=day)).date()
            for i in range(1, random.randrange(2, 6)):
                rec = next(recordings_iter)
                params['recording_id'] = rec.get('id')
                params['seconds_played'] = random.randrange(10, 600, 10)
                params['play_count'] = random.randrange(1, 100, 1)
                params['recording_type'] = rec.get('recording_type')
                params['event_id'] = rec.get('event_id')
                self.create(**params)

    def most_popular_audio(self, count=4, weekly=False, range_size=None):
        return self.get_queryset().most_popular_audio(
            weekly=weekly, range_size=range_size
        )[:count]

    def most_popular_video(self, count=4, weekly=False, range_size=None):
        return self.get_queryset().most_popular_video(
            weekly=weekly, range_size=range_size
        )[:count]

    def most_popular(self, count=4, weekly=False, range_size=None):
        return self.get_queryset().most_popular(
            weekly=weekly, range_size=range_size
        )[:count]


class UserVideoMetric(models.Model):
    recording_id = models.IntegerField(blank=False)
    user_id = models.IntegerField(blank=False)
    date = models.DateField(blank=False, default=timezone.now)
    last_ping = models.DateTimeField(auto_now=True)
    seconds_played = models.IntegerField(default=0)
    play_count = models.IntegerField(default=1)  # it gets created on the first play
    event_id = models.PositiveIntegerField(blank=False)
    event_date = models.DateTimeField(default=timezone.now)
    recording_type = models.CharField(max_length=1, choices=(('A', 'Audio'), ('V', 'Video')))

    objects = MetricsManager()

    class Meta:
        unique_together = ('recording_id', 'user_id', 'date')

    def __str__(self):
        return "V{0} U{1} D{2.year}/{2.month}/{2.day} C{3}".format(
            self.recording_id, self.user_id, self.date, self.seconds_played)
