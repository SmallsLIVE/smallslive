from operator import attrgetter
from collections import OrderedDict
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic.detail import DetailView
from natsort import natsorted
from oscar.core.loading import get_class, get_model
from oscar.apps.dashboard.reports import views as oscar_views
from events.models import Event, EventSet
from events.reports import DELETED_EVENT_ID_OFFSET


Line = get_class('order.models', 'Line')
Order = get_model('order', 'Order')


class _DeletedEventInfo(object):
    def __init__(self, title, venue_name, date):
        self.title = title
        self.date = date
        self._venue_name = venue_name

    def get_venue_name(self):
        return self._venue_name


class _DeletedEventSetInfo(object):
    start = None

    def __init__(self, event):
        self.event = event


from django.http import HttpResponseForbidden, Http404
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from oscar.core.loading import get_class
from oscar_apps.dashboard.reports.forms import ReportForm
GeneratorRepository = get_class('dashboard.reports.utils',
                                'GeneratorRepository')


class TicketsIndexView(oscar_views.IndexView):
    template_name = 'dashboard/reports/tickets_index.html'
    paginate_by = 25
    context_object_name = 'objects'
    report_form_class = ReportForm
    generator_repository = GeneratorRepository

    def _get_generator(self, form):
        code = form.cleaned_data['report_type']

        repo = self.generator_repository()
        generator_cls = repo.get_generator(code)
        if not generator_cls:
            raise Http404()

        download = form.cleaned_data['download']
        formatter = 'CSV' if download else 'HTML'

        return generator_cls(start_date=form.cleaned_data['date_from'],
                             end_date=form.cleaned_data['date_to'],
                             formatter=formatter)

    def get(self, request, *args, **kwargs):
        if 'report_type' in request.GET:
            report_type = request.GET.get('report_type')
            form = self.report_form_class(request.GET)
            if form.is_valid():
                generator = self._get_generator(form)
                if not generator.is_available_to(request.user):
                    return HttpResponseForbidden(_("You do not have access to"
                                                   " this report"))

                report = generator.generate()

                if form.cleaned_data['download']:
                    return report
                else:
                    self.set_list_view_attrs(generator, report)
                    context = self.get_context_data(object_list=self.queryset)
                    context['form'] = form
                    context['description'] = generator.report_description()
                    return self.render_to_response(context)
        else:
            form = self.report_form_class()
        return TemplateResponse(request, self.template_name, {'form': form})

    def set_list_view_attrs(self, generator, report):
        self.template_name = generator.filename()
        queryset = generator.filter_with_date_range(report)
        self.object_list = self.queryset = queryset


class TicketDetailsView(DetailView):
    template_name = 'dashboard/ticket_details.html'
    context_object_name = 'event_set'
    model = EventSet

    def get(self, request, *args, **kwargs):
        pk = int(self.kwargs['pk'])
        if pk >= DELETED_EVENT_ID_OFFSET:
            context = self.get_deleted_event_context(pk - DELETED_EVENT_ID_OFFSET)
            return self.render_to_response(context)
        return super(TicketDetailsView, self).get(request, *args, **kwargs)

    def get_deleted_event_context(self, line_pk):
        line = get_object_or_404(Line, pk=line_pk, product__isnull=True)
        lines = Line.objects.filter(
            order__order_type=Order.TICKET,
            product__isnull=True,
            title=line.title,
            partner_name=line.partner_name,
        ).exclude(
            status='Cancelled',
        ).exclude(
            status='Exchanged',
        ).select_related('order').order_by('order__last_name')

        tickets = [ticket for ticket in lines if ticket.order.status != 'Cancelled']
        total_tickets_sold = sum(ticket.quantity for ticket in tickets)

        date_placed = line.order.date_placed
        event = _DeletedEventInfo(
            line.title,
            line.partner_name,
            timezone.localtime(date_placed).date() if date_placed else None)
        event_set = _DeletedEventSetInfo(event)

        return {
            'event': event,
            'event_set': event_set,
            'show_data': [{
                'event_set': event_set,
                'tickets': tickets,
                'total_tickets_sold': total_tickets_sold,
            }],
        }

    def get_context_data(self, **kwargs):
        """
            Each product is now linked  to an EventSet (as tickets are sold for sets)
            Return context for the event so we can generate the report for all set
        """
        data = super(TicketDetailsView, self).get_context_data(**kwargs)

        # Populate products corresponding to each set of the event
        event = self.object.event
        event_sets = list(event.sets.all())
        products = []
        for event_set in event_sets:
            for ticket in event_set.tickets.all():
                products.append(ticket)

        # Get line objects so we can get the tickets name for the show
        show_data = []
        # Loop to keep the order and build a list of lists
        # [[person 1, person 2, ...], [person 1, ..] ]
        # One list per set.
        for product in products:
            set_list = []
            for line in Line.objects.filter(product=product).exclude(
                    status="Cancelled").exclude(status="Exchanged").order_by('order__last_name'):
                if line.order.status != 'Cancelled':
                    set_list.append(line)
            total_tickets_sold = sum([set.quantity for set in set_list])
            show_data.append({'event_set': product.event_set, 'tickets': set_list, 'total_tickets_sold': total_tickets_sold})

        data['show_data'] = show_data

        return data
