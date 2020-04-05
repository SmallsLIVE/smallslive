# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0028_auto_20200129_1538'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='misc_file',
            field=models.FileField(null=True, upload_to=b'misc_files', blank=True),
            preserve_default=True,
        ),
    ]
