from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.detail import DetailView
from braces.views import LoginRequiredMixin, UserPassesTestMixin, StaffuserRequiredMixin
from django_filters.views import FilterView
from haystack.inputs import Exact
from haystack.query import SearchQuerySet, RelatedSearchQuerySet
from haystack.views import FacetedSearchView, SearchView
from events.models import Event
from search.utils import facets_by_model_name
from .forms import ArtistAddForm, ArtistInviteForm, ArtistSearchForm
from .filters import ArtistFilter
from .models import Artist, Instrument


# not used right now, may be needed in the future if artist inviting will work the same way
# @user_passes_test(lambda u: u.is_superuser)
# def artist_add(request):
#     if request.method == 'POST':
#         artist_add_form = ArtistAddForm(request.POST, request.FILES)
#         artist_invite_form = ArtistInviteForm(request.POST)
#         forms = [artist_add_form, artist_invite_form]
#         if all([form.is_valid() for form in forms]):
#             print "valid"
#             print artist_add_form.cleaned_data['photo']
#             artist = artist_add_form.save()
#             email = artist_invite_form.cleaned_data.get('email')
#             invite_type = artist_invite_form.cleaned_data.get('invite_type')
#             if invite_type == ArtistInviteForm.INVITE_TYPE.standard_invite:
#                 artist.send_invitation(request, email)
#             elif invite_type == ArtistInviteForm.INVITE_TYPE.custom_invite:
#                 artist.send_invitation(request, email, artist_invite_form.cleaned_data.get('invite_text'))
#             messages.success(request, u"Artist {0} successfully added!".format(artist.full_name()))
#             return redirect('artist_add')
#     else:
#         artist_add_form = ArtistAddForm()
#         artist_invite_form = ArtistInviteForm()
#
#     return render(request, 'artists/artist_add.html', {
#         'artist_add_form': artist_add_form,
#         'artist_invite_form': artist_invite_form
#     })


# note - this is here only for Mezzrow compatibility
class ArtistAddView(StaffuserRequiredMixin, CreateView):
    model = Artist
    form_class = ArtistAddForm
    template_name = 'artists/artist_add.html'

artist_add = ArtistAddView.as_view()


class ArtistEditView(StaffuserRequiredMixin, UpdateView):
    model = Artist
    form_class = ArtistAddForm
    template_name = 'artists/artist_add.html'

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
        return Artist.objects.select_related('user').prefetch_related('instruments', 'events')


artist_list = ArtistFilterView.as_view()


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
        page_numbers = [n for n in xrange(startPage, endPage) if n > 0 and n <= paginator.num_pages]
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
        page_numbers = [n for n in xrange(startPage, endPage) if n > 0 and n <= paginator.num_pages]
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
