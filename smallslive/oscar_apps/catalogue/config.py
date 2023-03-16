#from oscar.apps.catalogue import config
from oscar.apps.catalogue import apps


class CatalogueConfig(apps.CatalogueConfig):
    name = 'oscar_apps.catalogue'
