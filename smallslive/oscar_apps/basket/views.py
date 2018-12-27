from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from oscar.apps.basket import views as basket_views
from oscar.apps.basket.views import apply_messages
from oscar_apps.partner.models import StockRecord


class BasketAddView(basket_views.BasketAddView):

    def _clean_basket(self, form):
        """Remove other types of items depending on what's being added.

        If user has added any item -> remove tickets, gift
        if user has added a gift -> remove tickets, items
        if user has added a ticket -> remove items, gifts, tickets from other venues.

        Basically, there can be only one of three 'types':

        1. Gift
        2. Ticket (from the same venue)
        3. Any other item (merchandise, cd's, etc.)

        """

        basket = self.request.basket

        added_class = form.product.product_class
        if added_class.name == 'Gift':
            basket.lines.all().delete()
        elif added_class.name == 'Ticket':
            # Remove anything from other venue
            venue_name = form.product.event_set.event.venue.name
            basket.lines.exclude(product__event_set__event__venue__name=venue_name).delete()
        else:
            # Remove tickets and gifts
            basket.lines.filter(product__product_class__name='Ticket').delete()
            basket.lines.filter(product__product_class__name='Gift').delete()

    def form_valid(self, form):
        print '****************************'
        print 'BasketAddView: form_valid'

        offers_before = self.request.basket.applied_offers()

        stockrecord_id = form.cleaned_data.get('stockrecord_id')
        try:
            stockrecord = StockRecord.objects.get(id=stockrecord_id)
        except StockRecord.DoesNotExist:
            stockrecord = None

        # Need to run some logic before adding
        self._clean_basket(form)

        basket = self.request.basket
        basket.add_product(
            form.product, form.cleaned_data['quantity'],
            form.cleaned_options(), stockrecord)

        # Do not show 'Added to your basket' message
        # for tickets and gifts
        if not basket.has_tickets() and not basket.has_gifts():
            messages.success(self.request, self.get_success_message(form),
                             extra_tags='safe noicon')

        if basket.has_tickets() or basket.has_gifts():
            print 'Cleaning messages'
            # Clear any other messages for tickets of gifts
            storage = messages.get_messages(self.request)
            for _ in storage:
                pass
            storage.used = True

        if not basket.has_tickets() and not basket.has_gifts():
            # Check for additional offer messages
            apply_messages(self.request, offers_before)

        # Send signal for basket addition
        self.add_signal.send(
            sender=self, product=form.product, user=self.request.user,
            request=self.request)

        if self.request.is_ajax():
            print 'return  200 (ajax)'
            return HttpResponse(status=200)
        else:
            return HttpResponseRedirect(self.get_success_url())
