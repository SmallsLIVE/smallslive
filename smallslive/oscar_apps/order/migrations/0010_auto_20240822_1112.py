# Generated by Django 3.2 on 2024-08-22 15:12

import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0005_auto_20240822_1112'),
        ('order', '0009_merge_0005_auto_20230323_1447_0008_auto_20190301_1035'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderdiscount',
            options={'ordering': ['pk'], 'verbose_name': 'Order Discount', 'verbose_name_plural': 'Order Discounts'},
        ),
        migrations.AlterModelOptions(
            name='ordernote',
            options={'ordering': ['-date_updated'], 'verbose_name': 'Order Note', 'verbose_name_plural': 'Order Notes'},
        ),
        migrations.RemoveField(
            model_name='line',
            name='est_dispatch_date',
        ),
        migrations.RemoveField(
            model_name='line',
            name='unit_cost_price',
        ),
        migrations.RemoveField(
            model_name='line',
            name='unit_retail_price',
        ),
        migrations.AlterField(
            model_name='billingaddress',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='communicationevent',
            name='event_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='communication.communicationeventtype', verbose_name='Event Type'),
        ),
        migrations.AlterField(
            model_name='communicationevent',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='line',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='lineattribute',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='lineattribute',
            name='value',
            field=models.JSONField(encoder=django.core.serializers.json.DjangoJSONEncoder, verbose_name='Value'),
        ),
        migrations.AlterField(
            model_name='lineprice',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='order',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='orderdiscount',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='ordernote',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='orderstatuschange',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='paymentevent',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='paymenteventquantity',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='paymenteventtype',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='shippingevent',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='shippingeventquantity',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='shippingeventtype',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.CreateModel(
            name='Surcharge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Surcharge')),
                ('code', models.CharField(max_length=128, verbose_name='Surcharge code')),
                ('incl_tax', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Surcharge (inc. tax)')),
                ('excl_tax', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Surcharge (excl. tax)')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='surcharges', to='order.order', verbose_name='Surcharges')),
            ],
            options={
                'ordering': ['pk'],
                'abstract': False,
            },
        ),
    ]
