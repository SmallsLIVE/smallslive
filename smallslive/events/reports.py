from collections import OrderedDict
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


class _DeletedEventSetRef(object):
    def __init__(self, set_id):
        self.id = set_id

    @property
    def first(self):
        return self


class DeletedEventTicketRow(object):
    id = 0
    subtitle = ''

    def __init__(self, title, venue_name, date, tickets_sold, detail_pk):
        self.title = title
        self.venue_name = venue_name
        self.date = date
        self.tickets_sold = tickets_sold
        self.sets = _DeletedEventSetRef(DELETED_EVENT_ID_OFFSET + detail_pk)

    def get_venue_name(self):
        return self.venue_name


class TicketReportGenerator(ReportGenerator):
    code = 'ticket_report'
    description = _("Tickets sold")
    date_range_field_name = 'start'

    formatters = {
        'HTML_formatter': TicketReportHTMLFormatter,
    }

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

    def _filter_lines_by_purchase_date(self, queryset):
        if self.start_date:
            start_datetime = timezone.make_aware(
                datetime.combine(self.start_date, time(0, 0)),
                timezone.get_default_timezone())
            start_datetime = start_datetime.astimezone(timezone.utc)
            queryset = queryset.filter(order__date_placed__gte=start_datetime)

        if self.end_date:
            end_of_end_date = datetime.combine(
                self.end_date, time(hour=23, minute=59, second=59))
            end_datetime = timezone.make_aware(
                end_of_end_date, timezone.get_default_timezone())
            end_datetime = end_datetime.astimezone(timezone.utc)
            queryset = queryset.filter(order__date_placed__lte=end_datetime)

        return queryset

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

        lines = self._filter_lines_by_purchase_date(lines).order_by('-order__date_placed')

        rows = OrderedDict()
        for line in lines:
            key = (line.title, line.partner_name)
            row = rows.get(key)
            if row is None:
                date_placed = line.order.date_placed
                rows[key] = DeletedEventTicketRow(
                    title=line.title,
                    venue_name=line.partner_name,
                    date=timezone.localtime(date_placed).date() if date_placed else None,
                    tickets_sold=line.quantity,
                    detail_pk=line.id,
                )
            else:
                row.tickets_sold += line.quantity

        return list(rows.values())

    def generate(self):
        events = Event._default_manager.filter(sets__tickets__isnull=False).distinct().order_by('-date')

        additional_data = {
            'start_date': self.start_date,
            'end_date': self.end_date
        }

        return self.formatter.generate_response(events, **additional_data)