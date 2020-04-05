from oscar.apps.partner import strategy
from oscar.apps.partner.strategy import StockRequired, DeferredTax, Structured


class UseMp3StockRecord():
    """
        Stockrecord selection mixin for use with the ``Structured`` base strategy.
        Uses non hd files.
        """

    def select_stockrecord(self, product):
        try:
            return product.stockrecords.filter(is_hd=False).first()
        except IndexError:
            return None


class Track(UseMp3StockRecord, StockRequired, DeferredTax, Structured):
    pass


class Selector(object):

    def strategy(self, request=None, user=None, **kwargs):
        return strategy.Default(request)

    def track_strategy(self, request=None, user=None, **kwargs):
        return Track(request)