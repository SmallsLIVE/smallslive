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

        date_from = self.request.GET.get('date_from', None)
        date_to = self.request.GET.get('date_to', None)

        if date_from:
            date_from = parser.parse(date_from, fuzzy=True)
            if not date_from.tzinfo:
                date_from = timezone.make_aware(
                    date_from, timezone.get_current_timezone())

        if date_to:
            date_to = parser.parse(date_to, fuzzy=True)
            if not date_to.tzinfo:
                date_to = timezone.make_aware(
                    date_to, timezone.get_current_timezone())

        return date_from, date_to

    def search(self, entity, search_terms, page=1, order=None,
               instrument=None, date_from=None, date_to=None,
               artist_search=None, artist_pk=None, venue=None, results_per_page=20,
               leader='all', search_input=None, all_media_status=False, only_published=True, artist_sort=None):

        # Checking if search_terms is not None.
        if not search_terms is None:
            search_terms = search_terms.strip()

        if artist_search:
            self.request.session['artist_search_value'] = artist_search

        search = SearchObject()

        if not search_input:
            search_input = search.process_input(search_terms, artist_search, instrument)
        terms, instruments, all_sax_instruments, partial_instruments, number_of_performers, \
            first_name, last_name, partial_name, artist_search, term_for_artist = search_input

        first = None
        last = None
        if entity == Artist:
            results_per_page = 24
            sqs = search.search_artist(
                terms, instruments, all_sax_instruments, partial_instruments,
                first_name, last_name, partial_name, artist_search, term_for_artist, artist_sort=artist_sort)

        elif entity == Event:
            sqs = search.search_event(
                terms, order, date_from, date_to,
                artist_pk=artist_pk, venue=venue,
                instruments=instruments, all_sax_instruments=all_sax_instruments,
                number_of_performers=number_of_performers,
                first_name=first_name, last_name=last_name, partial_name=partial_name,
                artist_search=artist_search, leader=leader, all_media_status=all_media_status,
                only_published=only_published)

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
            showing_results = '0'

        if entity == Event:
            return blocks, showing_results, paginator.num_pages, first, last, search_input
        else:
            return blocks, showing_results, paginator.num_pages, search_input


class UpcomingEventMixin(object):

    def get_upcoming_events_context_data(self, context):
        context['venues'] = Venue.objects.all()

        return context
