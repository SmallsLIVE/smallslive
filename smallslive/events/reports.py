from collections import OrderedDict
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.utils.translation import ugettext_lazy as _
from oscar.core.loading import get_class, get_model
from events.models import Event, EventSet
from datetime import datetime, time
from django.utils import timezone

ReportGenerator = get_class('dashboard.reports.reports', 'ReportGenerator')
ReportCSVFormatter = get_class('dashboard.reports.reports',
                               'ReportCSVFormatter')
ReportHTMLFormatter = get_class('dashboard.reports.reports',
                                'ReportHTMLFormatter')
Order = get_model('order', 'Order')
Line = get_model('order', 'Line')


class TicketReportHTMLFormatter(ReportHTMLFormatter):
    filename_template = 'dashboard/reports/partials/ticket_report.html'


DELETED_EVENT_ID_OFFSET = 10 ** 9

SOLD_TICKET_LINES = (
    Q(sets__tickets__line__order__order_type=Order.TICKET)
    & ~Q(sets__tickets__line__status__in=('Cancelled', 'Exchanged'))
    & ~Q(sets__tickets__line__order__status='Cancelled')
)


class _DeletedEventSetRef(object):
    def __init__(self, set_id):
        self.id = set_id

    @property
    def first(self):
        return self


def parse_set_time(set_time):
    if not set_time:
        return None
    try:
        return datetime.strptime(set_time, '%I:%M %p').time()
    except ValueError:
        return None


class DeletedEventTicketRow(object):
    id = 0
    subtitle = ''
    is_deleted = True

    def __init__(self, title, venue_name, date, detail_pk):
        self.title = title
        self.venue_name = venue_name
        self.date = date
        self.tickets_sold = 0
        self.sets = _DeletedEventSetRef(DELETED_EVENT_ID_OFFSET + detail_pk)
        self._set_times = []

    def add(self, quantity, set_time):
        self.tickets_sold += quantity
        if set_time and set_time not in self._set_times:
            self._set_times.append(set_time)

    def get_venue_name(self):
        return self.venue_name

    def get_range(self):
        times = [t for t in (parse_set_time(s) for s in self._set_times) if t]
        return (min(times), '') if times else ('', '')


class TicketReportGenerator(ReportGenerator):
    code = 'ticket_report'
    description = _("Tickets sold")
    date_range_field_name = 'start'

    formatters = {
        'HTML_formatter': TicketReportHTMLFormatter,
    }

    def __init__(self, **kwargs):
        super(TicketReportGenerator, self).__init__(**kwargs)
        self.venue = kwargs.get('venue')
        if self.venue:
            self.description = _('%(report_filter)s at %(venue)s') % {
                'report_filter': self.description,
                'venue': self.venue.name,
            }

    def total_tickets_sold(self, rows):
        return sum(row.tickets_sold for row in rows)

    def filter_with_venue(self, queryset):
        if not self.venue:
            return queryset

        return queryset.filter(venue=self.venue)

    def filter_with_date_range(self, queryset):
        """
        overriding the existing function
        """
        if not self.date_range_field_name:
            return queryset

        # After the start date
        if self.start_date:
            start_datetime = timezone.make_aware(
                datetime.combine(self.start_date, time(0, 0)),
                timezone.get_default_timezone())
            start_datetime = start_datetime.astimezone(timezone.utc)

            filter_kwargs = {
                "%s__gte" % self.date_range_field_name: start_datetime,
            }
            queryset = queryset.filter(**filter_kwargs)

        # Before the end of the end date
        if self.end_date:
            end_of_end_date = datetime.combine(
                self.end_date,
                time(hour=23, minute=59, second=59)
            )
            end_datetime = timezone.make_aware(end_of_end_date,
                                               timezone.get_default_timezone())
            end_datetime = end_datetime.astimezone(timezone.utc)
            filter_kwargs = {
                "%s__lte" % self.date_range_field_name: end_datetime,
            }
            queryset = queryset.filter(**filter_kwargs)

        return list(queryset) + self._deleted_event_rows()

    def _filter_lines_by_date(self, queryset):
        if not self.start_date and not self.end_date:
            return queryset

        event_date_range = Q()
        purchase_range = Q(event_date__isnull=True)

        if self.start_date:
            event_date_range &= Q(event_date__gte=self.start_date)
            start_datetime = timezone.make_aware(
                datetime.combine(self.start_date, time(0, 0)),
                timezone.get_default_timezone()).astimezone(timezone.utc)
            purchase_range &= Q(order__date_placed__gte=start_datetime)

        if self.end_date:
            event_date_range &= Q(event_date__lte=self.end_date)
            end_datetime = timezone.make_aware(
                datetime.combine(self.end_date, time(23, 59, 59)),
                timezone.get_default_timezone()).astimezone(timezone.utc)
            purchase_range &= Q(order__date_placed__lte=end_datetime)

        return queryset.filter(event_date_range | purchase_range)

    def _filter_lines_by_venue(self, queryset):
        if not self.venue:
            return queryset

        return queryset.filter(partner_name=self.venue.name)

    def _deleted_event_rows(self):
        lines = Line.objects.filter(
            order__order_type=Order.TICKET,
            product__isnull=True,
        ).exclude(
            status='Cancelled',
        ).exclude(
            status='Exchanged',
        ).exclude(
            order__status='Cancelled',
        ).select_related('order')

        lines = self._filter_lines_by_venue(lines)
        lines = self._filter_lines_by_date(lines).order_by('-order__date_placed')

        rows = OrderedDict()
        for line in lines:
            key = (line.title, line.partner_name, line.event_date)
            row = rows.get(key)
            if row is None:
                if line.event_date:
                    date = line.event_date
                else:
                    date_placed = line.order.date_placed
                    date = timezone.localtime(date_placed).date() if date_placed else None
                row = DeletedEventTicketRow(
                    title=line.title,
                    venue_name=line.partner_name,
                    date=date,
                    detail_pk=line.id,
                )
                rows[key] = row
            row.add(line.quantity, line.event_set_time)

        return list(rows.values())

    def generate(self):
        events = Event._default_manager.filter(
            sets__tickets__isnull=False,
        ).annotate(
            tickets_sold=Coalesce(
                Sum('sets__tickets__line__quantity', filter=SOLD_TICKET_LINES), 0),
        ).distinct().order_by('-date')

        events = self.filter_with_venue(events)

        additional_data = {
            'start_date': self.start_date,
            'end_date': self.end_date
        }

        return self.formatter.generate_response(events, **additional_data)