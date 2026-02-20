from typing import Optional

from events.models import Venue


def get_stripe_public_key_by_venue_name(venue_name: str) -> Optional[str]:
    try:
        current_venue = Venue.objects.get(name__iexact=venue_name)
        return current_venue.get_stripe_publishable_key
    except Exception:
        return None