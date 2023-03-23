# Generated by Django 2.2.28 on 2023-03-23 18:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0004_stockrecord_is_hd'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='partner',
            options={'ordering': ('name', 'code'), 'permissions': (('dashboard_access', 'Can access dashboard'),), 'verbose_name': 'Fulfillment partner', 'verbose_name_plural': 'Fulfillment partners'},
        ),
        migrations.AlterField(
            model_name='partner',
            name='name',
            field=models.CharField(blank=True, db_index=True, max_length=128, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='partner',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='partners', to=settings.AUTH_USER_MODEL, verbose_name='Users'),
        ),
        migrations.AlterField(
            model_name='partneraddress',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='address.Country', verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='partneraddress',
            name='partner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='partner.Partner', verbose_name='Partner'),
        ),
        migrations.AlterField(
            model_name='stockalert',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Date Created'),
        ),
        migrations.AlterField(
            model_name='stockalert',
            name='stockrecord',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to='partner.StockRecord', verbose_name='Stock Record'),
        ),
        migrations.AlterField(
            model_name='stockrecord',
            name='digital_download',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stock_record', to='multimedia.MediaFile'),
        ),
        migrations.AlterField(
            model_name='stockrecord',
            name='partner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stockrecords', to='partner.Partner', verbose_name='Partner'),
        ),
        migrations.AlterField(
            model_name='stockrecord',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stockrecords', to='catalogue.Product', verbose_name='Product'),
        ),
    ]
