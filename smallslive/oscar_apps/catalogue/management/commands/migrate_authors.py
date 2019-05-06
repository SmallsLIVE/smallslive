# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from django.core.management.base import NoArgsCommand
from artists.models import Artist, Instrument
from oscar_apps.catalogue.models import ArtistProduct, Product


class Command(NoArgsCommand):
    help = 'Migrate authors'

    def get_instruments(self):
        return list(Instrument.objects.values_list('name', flat=True)) + ['flugelhorn', 'ophone', 'tenor']

    def is_product_valid(self, product):

        if not product.short_description:
            return False

        product_types = [
            'Album',
            'Physical album',
            'Cellar live',
        ]

        product_type = product.get_product_class().name
        if product_type in product_types:
            return True

        return False

    def clean_line(self, line_text, instruments=[]):

        line_text = line_text.lower()
        for instrument in instruments:
            line_text = line_text.replace(instrument.lower(), '')
        line_text = line_text.replace('featuring', '')
        line_text = line_text.replace('engineered by', '')
        line_text = line_text.replace(':', '')
        line_text = line_text.replace('-', '')
        line_text = line_text.replace('(*)', '')
        line_text = line_text.replace('.', '')

        if not line_text:
            return line_text

        clean_front = line_text[0]
        while not clean_front.isalpha():
            line_text = line_text[1:]
            if line_text:
                clean_front = line_text[0]
            else:
                break

        if line_text:
            clean_tail = line_text[-1]
            while not clean_tail.isalpha():
                line_text = line_text[0:-1]
                if line_text:
                    clean_tail = line_text[-1]
                else:
                    break

        return line_text

    def find_instrument(self, instruments, line_text):
        for instrument in instruments:
            if instrument.lower() in line_text.lower():
                return Instrument.objects.filter(
                    name__iexact=instrument.lower()).first()

    def link_author(self, product, instrument, line_text):

        artist = Artist.objects.find_artist(line_text)

        if artist:
            artist_product = ArtistProduct.objects.get_or_create(
                artist=artist, product=product, instrument=instrument)

    def handle_noargs(self, *args, **options):
        """
        We need to translate the artists listed in short description
        to actual artist objects as authors.

        Strategy: clean lines. If instrument is in line, then artist must be present too.
        """
        instruments = self.get_instruments()
        for product in Product.objects.all():
            if self.is_product_valid(product):
                description = product.short_description
                lines = description.split('\n')
                for line in lines:
                    soup = BeautifulSoup(line, 'html.parser')
                    line_text = soup.text
                    instrument = self.find_instrument(instruments, line_text)
                    if instrument:
                        line_text = self.clean_line(line_text, instruments)
                        self.link_author(product, instrument, line_text)
                    else:
                        print 'Instrument not found: ', line_text
