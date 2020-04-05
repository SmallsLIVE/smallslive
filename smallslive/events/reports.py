from django.utils.translation import ugettext_lazy as _
from oscar.core.loading import get_class
from events.models import Event, EventSet

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

    formatters = {
        'HTML_formatter': TicketReportHTMLFormatter,
    }

    def generate(self):
        events = Event._default_manager.filter(sets__tickets__isnull=False).distinct().order_by('-date')

        additional_data = {
            'start_date': self.start_date,
            'end_date': self.end_date
        }

        return self.formatter.generate_response(events, **additional_data)