from django.utils.translation import ugettext_lazy as _
from oscar.core.loading import get_class
from events.models import Event, EventSet
from datetime import datetime, time
from django.utils import timezone

ReportGenerator = get_class('dashboard.reports.reports', 'ReportGenerator')
ReportCSVFormatter = get_class('dashboard.reports.reports',
                               'ReportCSVFormatter')
ReportHTMLFormatter = get_class('dashboard.reports.reports',
                                'ReportHTMLFormatter')


class TicketReportHTMLFormatter(ReportHTMLFormatter):
    filename_template = 'dashboard/reports/partials/ticket_report.html'


class TicketReportGenerator(ReportGenerator):
    code = 'ticket_report'
    description = _("Tickets sold")
    date_range_field_name = 'start'
    model_class = Event

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

        return queryset

    def generate(self):
        events = Event._default_manager.filter(sets__tickets__isnull=False).distinct().order_by('-date')

        additional_data = {
            'start_date': self.start_date,
            'end_date': self.end_date
        }

        return self.formatter.generate_response(events, **additional_data)