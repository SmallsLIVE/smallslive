from django.dispatch import receiver
from djstripe.models import Charge
from djstripe.signals import WEBHOOK_SIGNALS
from subscriptions.models import Donation


@receiver(WEBHOOK_SIGNALS['charge.succeeded'])
def charge_succeeded(sender, **kwargs):
    print 'Subscription -> '
    print sender
    print kwargs
    event = kwargs.get('event')
    if event:
        customer = event.customer
        charge = Charge.objects.filter(customer=customer).order_by('-id').first()
        print 'Charge ->', charge
        print 'Customer ->', customer
        print 'Reference ->', charge.stripe_id
        donation = Donation.objects.filter(reference=charge.stripe_id).first()
        print 'Donation:', donation
        if donation:
            donation.confirmed = True
            donation.save()
            # Donated by selecting a gift in the store
            print 'Donation saved!'
        else:
            donation = {
                'user': customer.subscriber,
                'currency': 'USD',
                'amount': charge.amount,
                'reference': charge.stripe_id,
                'confirmed': True,
            }
            print 'Donation object ->: ', donation
            Donation.objects.create(**donation)
            print 'Donation saved!s'
