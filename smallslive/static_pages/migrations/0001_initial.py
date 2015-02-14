# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def add_static_pages(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Site = apps.get_model("sites", "Site")
    site = Site.objects.first()
    FlatPage = apps.get_model("flatpages", "FlatPage")
    about_us = FlatPage.objects.create(url='/about-us/', title='About us',
                                       template_name='flatpages/about-us.html')
    about_us.sites.add(site)
    mission_statement = FlatPage.objects.create(url='/mission-statement/', title='Mission statement',
                                                template_name='flatpages/mission-statement.html')
    mission_statement.sites.add(site)
    contact = FlatPage.objects.create(url='/contact-and-info/', title='Contact and info',
                                      template_name='flatpages/contact-and-info.html')
    contact.sites.add(site)


class Migration(migrations.Migration):

    dependencies = [
        ('flatpages', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_static_pages)
    ]
