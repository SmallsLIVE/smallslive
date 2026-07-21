from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from oscar.core.loading import get_model

Line = get_model('order', 'Line')
Order = get_model('order', 'Order')


class Command(BaseCommand):
    help = ('Backfill event_set_time/event_date on ticket order lines that '
            'still have their product, so the data survives event deletion.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Only backfill lines placed within the last N days (default 30).')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=False,
            help='Report what would change without writing.')

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']

        lines = Line.objects.filter(
            order__order_type=Order.TICKET,
            product__event_set__isnull=False,
            event_set_time='',
        ).select_related('product__event_set__event')

        if days:
            since = timezone.now() - timedelta(days=days)
            lines = lines.filter(order__date_placed__gte=since)

        updated = 0
        for line in lines:
            event_set = line.product.event_set
            line.event_set_time = line.product.set or event_set.start.strftime('%-I:%M %p')
            line.event_date = event_set.event.date
            if not dry_run:
                line.save(update_fields=['event_set_time', 'event_date'])
            updated += 1

        prefix = '[dry-run] ' if dry_run else ''
        self.stdout.write(self.style.SUCCESS(
            '{}Backfilled {} ticket line(s).'.format(prefix, updated)))
