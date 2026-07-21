from oscar.apps.order.utils import OrderCreator as CoreOrderCreator


class OrderCreator(CoreOrderCreator):

    def create_line_models(self, order, basket_line, extra_line_fields=None):
        event_set = getattr(basket_line.product, 'event_set', None)
        if event_set:
            extra_line_fields = dict(extra_line_fields or {}, **{
                'event_set_time': basket_line.product.set or event_set.start.strftime('%-I:%M %p'),
                'event_date': event_set.event.date,
            })
        return super(OrderCreator, self).create_line_models(
            order, basket_line, extra_line_fields)
