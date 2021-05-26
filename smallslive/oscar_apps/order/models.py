from decimal import Decimal as D
from oscar.apps.order.signals import order_placed
from oscar.apps.order.abstract_models import AbstractOrder
from oscar.core.loading import get_model, get_class
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.db import models

CommunicationEventType = get_model('customer', 'CommunicationEventType')


class Order(AbstractOrder):

    GIFT = 'gift'
    REGULAR = 'regular'
    TICKET = 'ticket'

    ORDER_TYPE_CHOICES = (
        (GIFT, 'gift'),
        (REGULAR, 'regular'),
        (TICKET, 'ticket'),
    )

    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    order_type = models.CharField(max_length=32, choices=ORDER_TYPE_CHOICES, default=REGULAR)

    def has_physical_products(self):
        physical_count = self.lines.filter(product__product_class__requires_shipping=True).count()
        return physical_count > 0

    def physical_lines(self):
        return self.lines.select_related('product').filter(product__product_class__requires_shipping=True)

    def has_digital_products(self):
        digital_count = self.lines.filter(product__product_class__requires_shipping=False).count()
        return digital_count > 0

    def digital_lines(self):
        return self.lines.select_related('product').filter(product__product_class__requires_shipping=False)
    
    def has_tickets(self):
        tickets_count = self.lines.filter(product__product_class__name='Ticket').count()
        return tickets_count > 0

    def get_tickets_type(self):
        qs = self.lines.all().filter(product__product_class__name='Ticket')
        lines = list(qs)
        venue = None
        if lines:
            line = lines[0]
            venue = line.product.get_product_class().name.lower()

        return venue

    def get_tickets_venue(self):
        venue = None
        qs = self.lines.all().filter(product__product_class__name='Ticket')
        lines = list(qs)
        if lines:
            line = lines[0]
            venue = line.product.event_set.event.venue

        return venue

    def get_tickets_event(self):
        event = None
        qs = self.lines.all().filter(product__product_class__name='Ticket')
        lines = list(qs)
        if lines:
            line = lines[0]
            event = line.product.event_set.event

        return event
    
    def has_gift(self):
        gifts_count = self.lines.filter(product__categories__name='Gifts').count()

        return gifts_count > 0

    def has_catalog(self):

        count = self.lines.filter(product__categories__name='Music').count()
        if count > 0:
            return count

        count = self.lines.filter(product__parent__categories__name='Music').count()

        if count > 0:
            return count

        count = self.lines.filter(product__parent__categories__name='SmallsLIVE Catalog').count()

        return count > 0

    def get_deductable_total(self):
        total = D('0.00')
        for line in self.lines.all():
            try:
                deductable_amount = line.unit_price_incl_tax
                if line.unit_cost_price:
                    deductable_amount -=  line.unit_cost_price
                total += line.quantity * deductable_amount
            except ObjectDoesNotExist:
                # Handle situation where the product may have been deleted
                pass

        return total

    # signal receiving method to send email to fulfilment partner
    def send_fulfillment_request(sender, **kwargs):
        code = 'ORDER_PLACED'
        order = kwargs['order']
        user = kwargs['user']
        if order.has_physical_products():
            ctx = {
                'user': user,
                'order': order,
                'site': Site.objects.get_current(),
                'lines': order.lines.all()
            }
            messages = CommunicationEventType.objects.get_and_render(code, ctx)
            from_email = to_email = settings.OSCAR_FROM_EMAIL
            if messages['html']:
                email = EmailMultiAlternatives(messages['subject'],
                                               messages['body'],
                                               from_email=from_email,
                                               to=[to_email])
                email.attach_alternative(messages['html'], "text/html")
            else:
                email = EmailMessage(messages['subject'],
                                     messages['body'],
                                     from_email=from_email,
                                     to=[to_email])
            email.send()

    order_placed.connect(send_fulfillment_request)

# add import statement at the end, so that django imports overridden model names first
from oscar.apps.order.models import *
