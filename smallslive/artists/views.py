from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.detail import DetailView
from braces.views import StaffuserRequiredMixin
from django_filters.views import FilterView
from haystack.query import RelatedSearchQuerySet
from haystack.views import SearchView
from django.views.generic import View

from search.utils import facets_by_model_name
from .forms import ArtistAddForm, ArtistSearchForm
from .filters import ArtistFilter
from .models import Artist, Instrument
import csv


class ArtistAddView(StaffuserRequiredMixin, CreateView):
    model = Artist
    form_class = ArtistAddForm
    template_name = 'artists/artist_add.html'

    def get_context_data(self, **kwargs):
        context = super(ArtistAddView, self).get_context_data(**kwargs)
        context['action_name'] = 'add'
        return context

    def get_success_url(self):
        return reverse('artist_edit', kwargs={'pk': self.object.id, 'slug': self.object.slug})

artist_add = ArtistAddView.as_view()


class ArtistEditView(StaffuserRequiredMixin, UpdateView):
    model = Artist
    form_class = ArtistAddForm
    template_name = 'artists/artist_add.html'

    def get_context_data(self, **kwargs):
        context = super(ArtistEditView, self).get_context_data(**kwargs)
        context['action_name'] = 'edit'
        return context

    def get_success_url(self):
        return reverse('artist_edit', kwargs={'pk': self.object.id, 'slug': self.object.slug})

artist_edit = ArtistEditView.as_view()


class ArtistDetailView(DetailView):
    model = Artist
    context_object_name = 'artist'
    
    def get_context_data(self, **kwargs):
        context = super(ArtistDetailView, self).get_context_data(**kwargs)
        context['facebook_app_id'] = settings.FACEBOOK_APP_ID
        return context

artist_detail = ArtistDetailView.as_view()


class ArtistFilterView(StaffuserRequiredMixin, FilterView):
    context_object_name = 'artists'
    filterset_class = ArtistFilter
    paginate_by = 30
    template_name = 'artists/artist_list.html'

    def get_queryset(self):
        # faster event count compared to annotate()
        return Artist.objects.extra(
            {'events_count': 'SELECT COUNT(*) FROM events_gigplayed WHERE events_gigplayed.artist_id = artists_artist.id'}
        ).select_related('user').prefetch_related('instruments', 'events')

    def get_context_data(self, **kwargs):
        context = super(ArtistFilterView, self).get_context_data(**kwargs)
        paginator = context['paginator']
        page = paginator.page(self.request.GET.get('page', 1))
        adjacent_pages = 2
        startPage = max(page.number - adjacent_pages, 1)
        if startPage <= 3:
            startPage = 1
        endPage = page.number + adjacent_pages + 1
        if endPage >= paginator.num_pages - 1:
            endPage = paginator.num_pages + 1
        page_numbers = [n for n in range(startPage, endPage) if n > 0 and n <= paginator.num_pages]
        context.update({
            'page_numbers': page_numbers,
            'show_first': 1 not in page_numbers,
            'show_last': paginator.num_pages not in page_numbers,
            })

        return context


artist_list = ArtistFilterView.as_view()


class ArtistEmailsFilterView(ArtistFilterView):
    content_type = 'text/plain'
    paginate_by = 1000
    template_name = "artists/artist_list_emails.html"

    def get_queryset(self):
        return Artist.objects.exclude(user=None).select_related('user').values_list('user__email', flat=True).nocache()


artist_list_emails = ArtistEmailsFilterView.as_view()


class ArtistSearchView(SearchView):
    template = 'search/artist_search.html'

    def extra_context(self):
        context = {}
        paginator, page = self.build_page()
        adjacent_pages = 2
        startPage = max(page.number - adjacent_pages, 1)
        if startPage <= 3:
            startPage = 1
        endPage = page.number + adjacent_pages + 1
        if endPage >= paginator.num_pages - 1:
            endPage = paginator.num_pages + 1
        page_numbers = [n for n in xrange(startPage, endPage) if 0 < n <= paginator.num_pages]
        context.update({
            'page_numbers': page_numbers,
            'show_first': 1 not in page_numbers,
            'show_last': paginator.num_pages not in page_numbers,
            })

        context['counts'] = facets_by_model_name(self.sqs)

        instrument_id = self.request.GET.get('instrument')
        if instrument_id:
            search_term = Instrument.objects.get(id=instrument_id).name
        else:
            search_term = self.request.GET.get('q')
        context['search_term'] = search_term

        return context

    def get_results(self):
        self.sqs = super(ArtistSearchView, self).get_results().facet('model', order='term')
        if self.request.GET.get('instrument'):
            self.sqs = self.sqs.order_by('last_name')
        return self.sqs.models(Artist)

artist_search = ArtistSearchView(
    form_class=ArtistSearchForm,
    searchqueryset=RelatedSearchQuerySet()
)


class InstrumentSearchView(SearchView):
    template = 'search/instrument_search.html'

    def extra_context(self):
        context = {}
        paginator, page = self.build_page()
        adjacent_pages = 2
        startPage = max(page.number - adjacent_pages, 1)
        if startPage <= 3:
            startPage = 1
        endPage = page.number + adjacent_pages + 1
        if endPage >= paginator.num_pages - 1:
            endPage = paginator.num_pages + 1
        page_numbers = [n for n in xrange(startPage, endPage) if 0 < n <= paginator.num_pages]
        context.update({
            'page_numbers': page_numbers,
            'show_first': 1 not in page_numbers,
            'show_last': paginator.num_pages not in page_numbers,
            })

        context['counts'] = facets_by_model_name(self.sqs)
        context['search_term'] = self.request.GET.get('q')

        return context

    def get_results(self):
        self.sqs = super(InstrumentSearchView, self).get_results().facet('model', order='term')
        return self.sqs.models(Instrument)

instrument_search = InstrumentSearchView()


def artist_instrument_ajax(request, pk):
    instrument = Artist.objects.get(pk=pk).instruments.first()
    instrument_id = getattr(instrument, 'id', "")
    return HttpResponse(instrument_id)


class ArtistListCsvView(StaffuserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Create a response with CSV content
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="artist_list.csv"'

        # Create a CSV writer and write the header
        csv_writer = csv.writer(response)
        csv_writer.writerow([
            'ID',
            'Last Name',
            'First Name',
            'Shows'
        ])

        # Queryset
        artists = Artist.objects.extra({'events_count': 'SELECT COUNT(*) FROM events_gigplayed WHERE events_gigplayed.artist_id = artists_artist.id'}).select_related('user').prefetch_related('instruments', 'events')

        duplicate_artist = []
        seen = set()
        for artist in artists:
            name = artist.last_name + " " + artist.first_name
            csv_writer.writerow([
                artist.id,
                artist.last_name,
                artist.first_name,
                artist.events_count
            ])
            if name not in seen:
                seen.add(name)
            else:
                duplicate_artist.append(name)

        return response


download_artist_list_csv = ArtistListCsvView.as_view()


class ArtistArchiveCSVList(StaffuserRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        # Create a response with CSV content
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="artist_archive_list.csv"'

        # Create a CSV writer and write the header
        csv_writer = csv.writer(response)
        csv_writer.writerow([
            'First Name',
            'Last Name'
        ])

        all_artists = Artist.objects.all().order_by("last_name")

        for artist in all_artists:
            csv_writer.writerow([
                artist.first_name,
                artist.last_name,
            ])

        return response


download_archive_artist_list_csv = ArtistArchiveCSVList.as_view()
