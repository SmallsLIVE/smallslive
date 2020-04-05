# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_smallsuser_institution'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smallsuser',
            name='access_level',
            field=models.CharField(default=b'', max_length=30, blank=True, choices=[(b'48-hour pass', b'48-hour pass'), (b'Half Year Membership', b'Half Year Membership'), (b'Monthly Pass', b'Monthly Pass'), (b'Three Month Membership', b'Three Month Membership'), (b'admin', b'admin'), (b'basic membership', b'basic membership'), (b'benefactor_1', b'benefactor_1'), (b'benefactor_2', b'benefactor_2'), (b'benefactor_3', b'benefactor_3'), (b'member', b'member'), (b'musician', b'musician'), (b'smallslive membership', b'smallslive membership'), (b'supporter', b'supporter'), (b'trialMember', b'trialMember')]),
            preserve_default=True,
        ),
    ]
