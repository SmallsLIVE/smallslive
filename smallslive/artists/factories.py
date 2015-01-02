import factory


class ArtistFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'artists.Artist'

    first_name = factory.Sequence(lambda n: u'First#{0}'.format(n))
    last_name = factory.Sequence(lambda n: u'Last#{0}'.format(n))

    @factory.post_generation
    def instruments(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        self.instruments = InstrumentFactory.create_batch(3)


class ArtistWithEventsFactory(ArtistFactory):
    @factory.post_generation
    def events(self, create, extracted, **kwargs):
        from events.factories import GigPlayedFactory, PastGigPlayedFactory
        if not create:
            # Simple build, do nothing.
            return

        GigPlayedFactory.create_batch(3, artist=self)
        PastGigPlayedFactory.create_batch(2, artist=self)


class InstrumentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'artists.Instrument'

    name = factory.Iterator(['Trumpet', 'Bass', 'Piano'])
    abbreviation = factory.Iterator(['tr', 'b', 'p'])
