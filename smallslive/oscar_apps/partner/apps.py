#from oscar.apps.partner import config
from oscar.apps.partner import apps


class PartnerConfig(apps.PartnerConfig):
    label = 'partner'
    name = 'oscar_apps.partner'
    verbose_name = 'Partner'
