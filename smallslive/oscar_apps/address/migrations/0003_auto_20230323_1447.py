# Generated by Django 2.2.28 on 2023-03-23 18:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0002_load_countries'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='useraddress',
            options={'ordering': ['-num_orders_as_shipping_address'], 'verbose_name': 'User address', 'verbose_name_plural': 'User addresses'},
        ),
        migrations.RemoveField(
            model_name='useraddress',
            name='num_orders',
        ),
        migrations.AddField(
            model_name='useraddress',
            name='num_orders_as_billing_address',
            field=models.PositiveIntegerField(default=0, verbose_name='Number of Orders as Billing Address'),
        ),
        migrations.AddField(
            model_name='useraddress',
            name='num_orders_as_shipping_address',
            field=models.PositiveIntegerField(default=0, verbose_name='Number of Orders as Shipping Address'),
        ),
        migrations.AlterField(
            model_name='country',
            name='printable_name',
            field=models.CharField(db_index=True, max_length=128, verbose_name='Country name'),
        ),
        migrations.AlterField(
            model_name='useraddress',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='address.Country', verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='useraddress',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
    ]
