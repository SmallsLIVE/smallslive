import math

from paypal.payflow import facade as payflow_facade
from subscriptions.mixins import PayPalMixin
from subscriptions.mixins import StripeMixin
from oscar.apps.order.models import PaymentEventType
from oscar.apps.order.processing import EventHandler as CoreEventHandler


class EventHandler(CoreEventHandler, PayPalMixin, StripeMixin):

    def __init__(self, *args, **kwargs):
        self.tickets_type = None

        return super(EventHandler, self).__init__(*args, **kwargs)
    
    def cancel_stock_allocations(self, order, lines=None, line_quantities=None):
        """
        Cancel the stock allocations for the passed lines.

        If no lines/quantities are passed, do it for all lines.
        """
        if not lines:
            lines = order.lines.all()
        if not line_quantities:
            line_quantities = [line.quantity for line in lines]
        for line, qty in zip(lines, line_quantities):
            if line.status == 'Cancelled':
                if line.stockrecord:
                    line.stockrecord.cancel_allocation(qty)

    def refund_payment(self, order, reference, amount, currency, payment_type_name):
        refund_reference = None

        if 'paypal' in payment_type_name:
            refund_reference = self.refund_paypal_payment(
                reference,
                amount,
                currency,
                order)
        elif 'stripe' in payment_type_name:
            refund_reference = self.refund_stripe_payment(
                reference, order, int(amount * 100))

        return refund_reference

    def get_updated_order_line_data(self, active_order_line, refund_quantity):
        line_items = dict()
        new_quantity = active_order_line.quantity - refund_quantity

        line_items['quantity'] = new_quantity
        line_items['line_price_incl_tax'] = new_quantity * active_order_line.unit_price_incl_tax
        line_items['line_price_excl_tax'] = new_quantity * active_order_line.unit_price_excl_tax
        line_items['line_price_before_discounts_incl_tax'] = new_quantity * active_order_line.unit_price_excl_tax
        line_items['line_price_before_discounts_excl_tax'] = new_quantity * active_order_line.unit_price_excl_tax

        return line_items

    def handle_order_status_change(self, order, new_status, note_msg, refund_quantity=None):

        if new_status == 'Cancelled':
            payment_source = order.sources.first()
            reference = payment_source.reference
            amount = payment_source.amount_allocated
            currency = payment_source.currency
            payment_type_name = payment_source.source_type.name.lower()
            refund_reference = self.refund_payment(order, reference, amount, currency, payment_type_name)

            lines = order.stock_lines()
            # Change line status (which are  completed) to Cancelled too
            for line in lines:
                if line.status == 'Completed':
                    line.status = new_status
                    line.save()
            line_quantities = lines.values_list('quantity', flat=True)
            refund_event_type, _ = PaymentEventType.objects.get_or_create(name="Refunded")
            self.handle_payment_event(order, refund_event_type,
                                      order.total_incl_tax, lines,
                                      line_quantities, reference=refund_reference)
            self.cancel_stock_allocations(order, lines, line_quantities)

        if new_status == 'Refund':
            payment_source = order.sources.first()
            active_order_line = order.lines.filter(status='Completed').first()

            if active_order_line:
                reference = payment_source.reference
                refund_amount = active_order_line.unit_price_incl_tax * refund_quantity

                currency = payment_source.currency
                payment_type_name = payment_source.source_type.name.lower()
                refund_reference = self.refund_payment(order, reference, refund_amount, currency, payment_type_name)

                lines = order.stock_lines()
                updated_order_line = self.get_updated_order_line_data(active_order_line, refund_quantity)

                lines.filter(status='Completed').update(**updated_order_line)

                # for line in lines:
                #     if line.status == 'Completed':
                #         line.quantity = line.quantity - refund_quantity
                #         line.save()

                refund_event_type, _ = PaymentEventType.objects.get_or_create(name="Refunded")
                self.handle_payment_event(order, refund_event_type,
                                          refund_amount, lines,
                                          [refund_quantity], reference=refund_reference)

                print("Help me")


        # order.set_status(new_status)
        # TODO: undo donations and library if necessary

