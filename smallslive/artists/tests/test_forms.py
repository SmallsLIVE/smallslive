import pytest
from artists.models import Artist
from ..factories import InstrumentFactory
from ..forms import ArtistAddForm

@pytest.fixture()
def correct_request():
    return {
        'salutation': 'Mr.',
        'first_name': 'Spike',
        'last_name': 'Wilner',
        'instruments': [1, 2],
        'biography': 'Test biography',
        'website': 'http://spikewilner.com',
        'photo': ''
    }

@pytest.fixture()
def wrong_request():
    return {
        'salutation': '',
        'first_name': '',
        'last_name': '',
        'instruments': None,
        'biography': '',
        'website': '',
        'photo': ''
    }

@pytest.mark.django_db()
class TestArtistAddForm:
    def test_form_renders_inputs_correctly(self):
        artist_add_form = ArtistAddForm()
        
        form_output = artist_add_form.as_p()
        assert "Photo (portrait-style JPG w/ instrument preferred)" in form_output
        assert "<form" not in form_output

    def test_form_accepts_valid_input(self, correct_request):
        form = ArtistAddForm(correct_request)
        InstrumentFactory.create_batch(3)

        form_valid = form.is_valid()
        assert not form.errors
        assert form_valid is True

        artist = form.save()
        assert artist.id == 1
        assert Artist.objects.count() == 1
        assert artist.first_name == "Spike"
        assert artist.instruments.count() == 2

    def test_form_fails_on_wrong_input(self, wrong_request):
        form = ArtistAddForm(wrong_request)
        InstrumentFactory.create_batch(3)

        form_valid = form.is_valid()
        assert not form_valid

        assert "This field is required." in form.errors['first_name']
        assert "This field is required." in form.errors['last_name']
