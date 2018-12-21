from oscar.apps.order.models import PaymentEventType
from oscar.apps.order.processing import EventHandler as CoreEventHandler
from paypal.payflow import facade as payflow_facade
from paypal.express.models import ExpressTransaction
from paypal.express.gateway import DO_EXPRESS_CHECKOUT, refund_txn


class EventHandler(CoreEventHandler):
    def handle_order_status_change(self, order, new_status):
        if new_status == "Cancelled":
            payment_source = order.sources.first()
            if payment_source.source_type.name == "Credit Card":
                payflow_facade.credit(order.number, amt=order.total_incl_tax)
            else:
                reference_number = order.payment_events.get(event_type__name="Settled").reference
                transaction = ExpressTransaction.objects.get(method=DO_EXPRESS_CHECKOUT,
                                                             correlation_id=reference_number)
                refund_txn(transaction.value('PAYMENTINFO_0_TRANSACTIONID'))
            lines = order.lines.all()
            line_quantities = lines.values_list('quantity', flat=True)
            refund_event = PaymentEventType.objects.get(name="Refunded")
            self.handle_payment_event(order, refund_event, order.total_incl_tax, lines, line_quantities)
            self.cancel_stock_allocations(order, lines, line_quantities)
        order.set_status(new_status)
