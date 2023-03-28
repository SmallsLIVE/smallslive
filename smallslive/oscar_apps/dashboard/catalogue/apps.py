from oscar.apps.dashboard.catalogue import apps


class CatalogueDashboardConfig(apps.CatalogueDashboardConfig):
    label = 'catalogue_dashboard'
    name = 'oscar_apps.dashboard.catalogue'
    verbose_name = 'Catalogue'
