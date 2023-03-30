# Generated by Django 2.2.28 on 2023-03-23 18:47

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderanditemcharges',
            name='countries',
            field=models.ManyToManyField(blank=True, to='address.Country', verbose_name='Countries'),
        ),
        migrations.AlterField(
            model_name='orderanditemcharges',
            name='name',
            field=models.CharField(db_index=True, max_length=128, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='weightband',
            name='method',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bands', to='shipping.WeightBased', verbose_name='Method'),
        ),
        migrations.AlterField(
            model_name='weightband',
            name='upper_limit',
            field=models.DecimalField(db_index=True, decimal_places=3, help_text='Enter upper limit of this weight band in kg. The lower limit will be determined by the other weight bands.', max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Upper Limit'),
        ),
        migrations.AlterField(
            model_name='weightbased',
            name='countries',
            field=models.ManyToManyField(blank=True, to='address.Country', verbose_name='Countries'),
        ),
        migrations.AlterField(
            model_name='weightbased',
            name='name',
            field=models.CharField(db_index=True, max_length=128, unique=True, verbose_name='Name'),
        ),
    ]