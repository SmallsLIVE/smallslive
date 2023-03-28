import oscar.apps.dashboard.reports.apps as apps


class ReportsDashboardConfig(apps.ReportsDashboardConfig):
    label = 'reports_dashboard'
    name = 'oscar_apps.dashboard.reports'
    verbose_name = 'Reports dashboard'
