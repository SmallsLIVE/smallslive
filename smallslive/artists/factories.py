import factory


class ArtistFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'artists.Artist'

    first_name = factory.Sequence(lambda n: u'First#{0}'.format(n))
    last_name = factory.Sequence(lambda n: u'Last#{0}'.format(n))
