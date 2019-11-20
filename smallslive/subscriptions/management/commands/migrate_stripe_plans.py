
from optparse import make_option
from djstripe.models import Customer, Charge, Plan
from django.core.management.base import BaseCommand
from users.models import SmallsUser


class Command(BaseCommand):
    args = "<user_email>"
    help = 'Migrates plans from Basic to Archive Access'

    option_list = BaseCommand.option_list + (
        make_option('--user-email',
                    action='store',
                    dest='user_email',
                    default='all',
                    help='user email / all for all'),
        make_option('--source-plan',
                    action='store',
                    dest='source_plan',
                    help='Source Stripe plan id'),
    )

    def handle(self, *args, **options):

        user_email = options.get('user_email')
        source_plan = options.get('source_plan')

        if user_email == 'all':
            users = SmallsUser.objects.filter(customer__isnull=False)
        else:
            users = SmallsUser.objects.filter(email=user_email)

        for user in users.order_by('-pk')[:1]:
            customer = Customer.objects.get(subscriber=user)
            if customer.has_active_subscription():
                try:
                    print 'Customer: ', customer, user.pk
                    print 'Plan: ', customer.current_subscription.plan
                    for subscription in customer.stripe_customer.subscriptions:
                        print subscription
                except Plan.DoesNotExist:
                    print 'Plan not found !!'

