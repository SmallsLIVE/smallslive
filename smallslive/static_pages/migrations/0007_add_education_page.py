# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def add_education_page(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Site = apps.get_model("sites", "Site")
    site = Site.objects.first()
    FlatPage = apps.get_model("flatpages", "FlatPage")
    press = FlatPage.objects.create(url='/education/', title='Education',
                                       template_name='flatpages/education.html')
    press.sites.add(site)
    press.content = """<p>
        Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Nam liber tempor cum soluta nobis eleifend option congue nihil imperdiet doming id quod mazim placerat facer possim assum.
    </p>
    <p>
        Typi non habent claritatem insitam; est usus legentis in iis qui facit eorum claritatem. Investigationes demonstraverunt lectores legere me lius quod ii legunt saepius. Claritas est etiam processus dynamicus, qui sequitur mutationem consuetudium lectorum. Mirum est notare quam littera gothica, quam nunc putamus parum claram, anteposuerit litterarum formas humanitatis per seacula quarta decima et quinta decima. Eodem modo typi, qui nunc nobis videntur parum clari, fiant sollemnes in futurum.
    </p>
    """
    press.save()


class Migration(migrations.Migration):

    dependencies = [
        ('static_pages', '0006_add_mezzrow_page'),
    ]

    operations = [
        migrations.RunPython(add_education_page)
    ]
