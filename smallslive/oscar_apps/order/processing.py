from paypal.payflow import facade as payflow_facade
from subscriptions.mixins import PayPalMixin
from subscriptions.mixins import StripeMixin
from oscar.apps.order.models import PaymentEventType
from oscar.apps.order.processing import EventHandler as CoreEventHandler


class EventHandler(CoreEventHandler, PayPalMixin, StripeMixin):

    def __init__(self, *args, **kwargs):
        self.tickets_type = None

        return super(EventHandler, self).__init__(*args, **kwargs)

    def handle_order_status_change(self, order, new_status, note_msg):

        if new_status == 'Cancelled':
            payment_source = order.sources.first()
            reference = payment_source.reference
            amount = payment_source.amount_allocated
            currency = payment_source.currency
            payment_type_name = payment_source.source_type.name.lower()
            if 'paypal' in payment_type_name:
                refund_reference = self.refund_paypal_payment(
                    reference,
                    amount,
                    currency,
                    order)
            elif 'stripe' in payment_type_name:
                refund_reference = self.refund_stripe_payment(
                    reference, order)

            lines = order.stock_lines()
            line_quantities = lines.values_list('quantity', flat=True)
            refund_event_type, _ = PaymentEventType.objects.get_or_create(name="Refunded")
            self.handle_payment_event(order, refund_event_type,
                                      order.total_incl_tax, lines,
                                      line_quantities, reference=refund_reference)
            self.cancel_stock_allocations(order, lines, line_quantities)
        order.set_status(new_status)
        # TODO: undo donations and library if necessary

