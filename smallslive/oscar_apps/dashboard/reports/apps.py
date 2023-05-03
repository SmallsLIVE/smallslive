import oscar.apps.dashboard.reports.apps as apps
from django.conf.urls import url
from django.utils.translation import gettext_lazy as _
from oscar.core.loading import get_class
#from oscar_apps.dashboard.reports import views as report_views
#from .views import TicketDetailsView

class ReportsDashboardConfig(apps.ReportsDashboardConfig):
    label = 'reports_dashboard'
    name = 'oscar_apps.dashboard.reports'
    verbose_name = 'Reports dashboard'


    # def get_urls(self):
    #
    #     urls = [
    #         url(r'^ticket-details/(?P<pk>\d+)/$', TicketDetailsView.as_view(), name='ticket_details'),
    #         url(r'^$', TicketsIndexView.as_view(), name='reports-index'),
    #         url(r'^tickets$', self.tickets_index_view.as_view(), name='tickets-report-index'),
    #     ]
    #     return self.post_process_urls(patterns('', *urls))
    #

    def ready(self):
        self.index_view = get_class('dashboard.reports.views', 'TicketsIndexView')
        self.ticketdetailsview = get_class('dashboard.reports.views', 'TicketDetailsView')

    def get_urls(self):
        urls = [
            url(r'^$', self.index_view.as_view(), name='reports-index'),
            url(r'^ticket-details/(?P<pk>\d+)/$', self.ticketdetailsview.as_view(), name='ticket_details'),
        ]
        return self.post_process_urls(urls)