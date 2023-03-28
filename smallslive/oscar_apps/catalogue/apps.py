from oscar.apps.catalogue import apps


class CatalogueConfig(apps.CatalogueConfig):
    label = 'catalogue'
    name = 'oscar_apps.catalogue'
    verbose_name = 'Catalogue'
