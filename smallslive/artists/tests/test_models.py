import pytest
from django.core import mail
from users.models import SmallsEmailAddress
from ..factories import ArtistFactory


@pytest.fixture(scope="module")
def artist_factory():
    return ArtistFactory


@pytest.fixture(autouse=True)
@pytest.mark.django_db()
def reset_model_counters():
    ArtistFactory.reset_sequence()

@pytest.mark.django_db()
class TestArtist:
    def test_get_absolute_url(self, artist_factory):
        artist = artist_factory.create()
        assert artist.get_absolute_url() == u'/artists/1/'

        another_artist = artist_factory.create()
        assert another_artist.get_absolute_url() == u'/artists/2/'

    def test_full_name(self, artist_factory):
        artist = artist_factory.build()
        assert artist.full_name() == u'First#1 Last#1'

        another_artist = artist_factory.build()
        assert another_artist.full_name() == u'First#2 Last#2'

    def test_send_invitation(self, artist_factory, django_user_model, rf):
        # artist without a User model assigned
        request = rf.get('artist_add')
        email = "test@example.com"
        artist = artist_factory.build()
        artist.send_invitation(request, email=email)
        assert artist.user.id == 1
        assert SmallsEmailAddress.objects.filter(email=email, user=artist.user).count() == 1
        assert len(mail.outbox) == 1
        assert "Confirm E-mail Address" in mail.outbox[0].subject

        # User already exists in the DB
        email = "test2@example.com"
        django_user_model.objects.create_user(email=email)
        another_artist = artist_factory.build()
        another_artist.send_invitation(request, email=email)
        assert another_artist.user.id == 2
        assert SmallsEmailAddress.objects.filter(email=email, user=another_artist.user).count() == 1
        assert len(mail.outbox) == 2
        assert "Confirm E-mail Address" in mail.outbox[1].subject
