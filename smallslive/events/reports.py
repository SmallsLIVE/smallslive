from django.utils.translation import ugettext_lazy as _
from oscar.core.loading import get_class
from events.models import EventSet

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
        event_sets = EventSet._default_manager.filter(tickets__isnull=False).order_by('-event__date')

        additional_data = {
            'start_date': self.start_date,
            'end_date': self.end_date
        }

        return self.formatter.generate_response(event_sets, **additional_data)