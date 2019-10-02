from collections import OrderedDict
from dateutil import parser
from itertools import groupby
from django.core.paginator import EmptyPage, Paginator
from django.utils import timezone
from django.utils.timezone import timedelta
from django.db.models import Q

from artists.models import Artist, Instrument
from events.models import Event, Venue, RANGE_MONTH

from .search import SearchObject


class SearchMixin(object):

    def get_filter_dates(self, referer):

        remember_date = self.request.GET.get('remember_date') == 'True'

        date_from = None
        if referer and ('artist_pk' in referer or 'events' in referer) or remember_date:
            date_from = self.request.session.get('search_date_from')
        else:
            if 'search_date_from' in self.request.session:
                del self.request.session['search_date_from']
        if date_from:
            date_from = parser.parse(date_from, fuzzy=True)
            if not date_from.tzinfo:
                date_from = timezone.make_aware(
                    date_from, timezone.get_current_timezone())

        date_to = None
        if referer and ('artist_pk' in referer or 'events' in referer) or remember_date:
            date_to = self.request.session.get('search_date_to')
        else:
            if 'search_date_to' in self.request.session:
                del self.request.session['search_date_to']
        if date_to:
            date_to = parser.parse(date_to, fuzzy=True)
            if not date_to.tzinfo:
                date_to = timezone.make_aware(
                    date_to, timezone.get_current_timezone())

        return date_from, date_to

    def search(self, entity, search_terms, page=1, order=None,
               instrument=None, date_from=None, date_to=None,
               artist_search=None, artist_pk=None, venue=None, results_per_page=60):

        search_terms = search_terms.strip()

        print '*************** SearchMixin.search ********************'
        print 'main_search: ', search_terms
        print 'order: ', order
        print 'page: ', page
        print 'instrument: ', instrument
        print 'date_from: ', date_from
        print 'date_to: ', date_to
        print 'venue: ', venue
        print 'artist_search: ', artist_search
        print '-------------------------------------------------------'

        search = SearchObject()

        search_input = search.process_input(search_terms, artist_search, instrument)
        terms, instruments, partial_instruments, number_of_performers, \
            first_name, last_name, partial_name, artist_search = search_input

        print 'terms: ', terms
        print 'instruments: ', instruments
        print 'partial instruments: ', partial_instruments
        print 'performers: ', number_of_performers
        print 'first: ', first_name
        print 'last: ', last_name
        print 'partial name: ', partial_name
        print 'entity: ', entity

        first = None
        last = None
        if entity == Artist:
            results_per_page = 24
            sqs = search.search_artist(
                terms, instruments, partial_instruments, first_name, last_name, partial_name, artist_search)

        elif entity == Event:

            sqs = search.search_event(
                terms, order, date_from, date_to,
                artist_pk=artist_pk, venue=venue,
                instruments=instruments, number_of_performers=number_of_performers,
                first_name=first_name, last_name=last_name, partial_name=partial_name)

            if not self.request.user.is_superuser:
                sqs = sqs.filter(Q(state=Event.STATUS.Published) | Q(state=Event.STATUS.Cancelled))

            first = sqs.first()
            last = sqs.last()

        blocks = []
        block = []

        paginator = Paginator(sqs, results_per_page)

        try:
            objects = paginator.page(page).object_list
        except EmptyPage:
            objects = []

        for item in objects:
            block.append(item)

            if len(block) == 6 and entity == Artist:
                blocks.append(block)
                block = []

        if block:
            blocks.append(block)

        if paginator.count:
            showing_results = paginator.count
        else:
            showing_results = 'NO RESULTS'

        if entity == Event:
            return blocks, showing_results, paginator.num_pages, first, last
        else:
            return blocks, showing_results, paginator.num_pages


class UpcomingEventMixin(object):

    def get_upcoming_events_context_data(self, context):
        date_range_start = timezone.localtime(timezone.now())
        # if it's not night when events are still hapenning, show next day
        if date_range_start.hour > 6:
            date_range_start += timedelta(days=1)
        # don't show last nights events that are technically today
        date_range_start = date_range_start.replace(hour=10)
        events = Event.objects.filter(start__gte=date_range_start).order_by('start')
        if not self.request.user.is_staff:
            events = events.exclude(state=Event.STATUS.Draft)

        venue = self.request.GET.get('venue')
        if venue is not None:
            venue_id = int(venue)
            events = events.filter(venue__id=venue_id)
            context['venue_selected'] = venue_id

        # 30 events should be enough to show next 7 days with events
        events = events[:30]
        dates = {}
        for k, g in groupby(events, lambda e: e.listing_date()):
            dates[k] = list(g)
        sorted_dates = OrderedDict(sorted(dates.items(), key=lambda d: d[0])).items()[:7]
        context['next_7_days'] = sorted_dates
        most_recent = Event.objects.most_recent()[:20]
        if len(most_recent):
            context['new_in_archive'] = most_recent
        else:
            context['new_in_archive'] = Event.objects.exclude(
                state=Event.STATUS.Draft
            ).order_by('-start')[:20]
        context['venues'] = Venue.objects.all()
        return context
