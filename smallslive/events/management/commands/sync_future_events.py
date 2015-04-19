from django.core.management.base import NoArgsCommand
from artists.models import Artist
from events.models import Event, GigPlayed


class Command(NoArgsCommand):
    help = 'Syncs the future events with the production server'

    def handle_noargs(self, *args, **options):
        for e in Event.objects.using('heroku').upcoming():
            try:
                Event.objects.get(id=e.id)
            except Event.DoesNotExist:
                event = Event.objects.create(
                    id=e.id,
                    title=e.title,
                    start=e.start,
                    end=e.end,
                    description=e.description,
                    state=e.state,
                    slug=e.slug,
                    photo=e.photo
                )
                print event.title
                for performer in e.performers.all():
                    Artist.objects.get_or_create(
                        id=performer.id, defaults={
                            'first_name': performer.first_name,
                            'last_name': performer.last_name
                        }
                    )
                for gig in e.artists_gig_info.all():
                    GigPlayed.objects.get_or_create(
                        id=gig.id,
                        event=gig.event,
                        artist=gig.artist,
                        role=gig.role,
                        is_leader=gig.is_leader,
                        sort_order=gig.sort_order
                    )
