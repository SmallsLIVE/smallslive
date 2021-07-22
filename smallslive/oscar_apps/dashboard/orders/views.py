from django.core.urlresolvers import reverse
from django.views.generic import FormView, View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import BaseFormView
from oscar.apps.dashboard.orders.views import LineDetailView as CoreLineDetailView
from .forms import TicketExchangeSelectForm
from oscar_apps.order.processing import EventHandler
from oscar_apps.order.models import PaymentEventType, Line, Order


class LineDetailGetView(CoreLineDetailView):
    def get_context_data(self, **kwargs):
        data = super(LineDetailGetView, self).get_context_data(**kwargs)
        data['form'] = TicketExchangeSelectForm(old_ticket_id=self.object.id)
        return data


class TicketExchangeView(SingleObjectMixin, BaseFormView):
    form_class = TicketExchangeSelectForm
    model = Order
    slug_field = 'number'
    slug_url_kwarg = 'number'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        response = super(TicketExchangeView, self).post(request, *args, **kwargs)
        old_ticket = Line.objects.get(id=self.old_ticket_id)
        # https://github.com/django-oscar/django-oscar/blob/0.7.2/oscar/apps/catalogue/abstract_models.py#L397
        # TODO: if no stocks, no error is shown to the user. Exchange will not work.
        if self.new_ticket.stockrecords.first().net_stock_level >= old_ticket.quantity:
            exchange_event, created = PaymentEventType.objects.get_or_create(name="Exchanged")
            sold_event, created = PaymentEventType.objects.get_or_create(name="Sold")
            old_ticket.set_status("Exchanged")
            handler = EventHandler(request.user)
            handler.handle_payment_event(
                self.object, exchange_event, old_ticket.line_price_incl_tax, [old_ticket], [old_ticket.quantity])
            new_line = self._get_new_ticket(old_ticket, self.new_ticket)
            handler.handle_payment_event(
                self.object, sold_event, new_line.line_price_incl_tax, [new_line], [new_line.quantity])
        return response

    def form_valid(self, form):
        self.old_ticket_id = form.cleaned_data['old_ticket_id']
        self.new_ticket = form.cleaned_data['ticket']
        return super(TicketExchangeView, self).form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:order-detail', kwargs={'number': self.object.number})

    def _get_new_ticket(self, old_line, new_ticket):
        old_sku = old_line.stockrecord
        sku = new_ticket.stockrecords.first()
        new_line = old_line
        new_line.id = None
        new_line.product = new_ticket
        new_line.sku = sku
        new_line.partner_sku = sku.partner_sku
        new_line.status = "Completed"
        new_line.title = new_ticket.title
        new_line.save()
        sku.allocate(new_line.quantity)
        old_sku.cancel_allocation(new_line.quantity)
        return new_line


class LineDetailView(View):

    def get(self, request, *args, **kwargs):
        view = LineDetailGetView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = TicketExchangeView.as_view()
        return view(request, *args, **kwargs)
