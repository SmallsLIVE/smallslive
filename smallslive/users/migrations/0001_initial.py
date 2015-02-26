# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SmallsUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(unique=True, max_length=75)),
                ('first_name', models.CharField(max_length=50, blank=True)),
                ('last_name', models.CharField(max_length=50, blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text=b'Designates whether the user can log into this admin site.')),
                ('is_active', models.BooleanField(default=True, help_text=b'Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('photo', models.ImageField(upload_to=b'user_photos', blank=True)),
                ('access_level', models.CharField(default=b'', max_length=30, blank=True, choices=[(b'48-hour pass', b'48-hour pass'), (b'Half Year Membership', b'Half Year Membership'), (b'Monthly Pass', b'Monthly Pass'), (b'Three Month Membership', b'Three Month Membership'), (b'admin', b'admin'), (b'basic membership', b'basic membership'), (b'member', b'member'), (b'musician', b'musician'), (b'smallslive membership', b'smallslive membership'), (b'trialMember', b'trialMember')])),
                ('login_count', models.IntegerField(default=0)),
                ('accept_agreement', models.BooleanField(default=False)),
                ('renewal_date', models.DateField(null=True, blank=True)),
                ('subscription_price', models.IntegerField(null=True, blank=True)),
                ('company_name', models.CharField(max_length=150, blank=True)),
                ('address_1', models.CharField(max_length=100, blank=True)),
                ('address_2', models.CharField(max_length=100, blank=True)),
                ('city', models.CharField(max_length=100, blank=True)),
                ('state', models.CharField(max_length=50, blank=True)),
                ('zip', models.CharField(max_length=100, blank=True)),
                ('country', models.CharField(max_length=100, blank=True)),
                ('phone_1', models.CharField(max_length=100, blank=True)),
                ('website', models.CharField(max_length=100, blank=True)),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model,),
        ),
    ]
