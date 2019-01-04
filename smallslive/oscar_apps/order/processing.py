from subscriptions.mixins import PayPalMixin
from subscriptions.mixins import StripeMixin
from oscar.apps.order.models import PaymentEventType
from oscar.apps.order.processing import EventHandler as CoreEventHandler


class EventHandler(CoreEventHandler, PayPalMixin, StripeMixin):

    def handle_order_status_change(self, order, new_status, note_msg):

        if new_status == "Cancelled":
            payment_source = order.sources.first()
            reference = payment_source.reference
            amount = payment_source.amount_allocated
            currency = payment_source.currency
            if payment_source.source_type.name == "Credit Card":
                refund_reference = self.refund_stripe_payment(
                    reference,
                    amount)
            else:
                refund_reference = self.refund_paypal_payment(
                    reference,
                    amount,
                    currency)

            lines = order.lines.all()
            line_quantities = lines.values_list('quantity', flat=True)
            refund_event_type, _ = PaymentEventType.objects.get_or_create(name="Refunded")
            self.handle_payment_event(order, refund_event_type,
                                      order.total_incl_tax, lines,
                                      line_quantities, reference=refund_reference)
            self.cancel_stock_allocations(order, lines, line_quantities)
        order.set_status(new_status)
