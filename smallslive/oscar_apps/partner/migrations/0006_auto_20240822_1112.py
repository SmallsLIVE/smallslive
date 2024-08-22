# Generated by Django 3.2 on 2024-08-22 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0005_auto_20230323_1447'),
    ]

    operations = [
        migrations.RemoveField(model_name='stockrecord', name='cost_price', ),
        migrations.RemoveField(model_name='stockrecord', name='price_retail', ),
        migrations.AlterField(model_name='stockrecord', name='price_excl_tax',
                              field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True,
                                                        verbose_name='Price'), ),
        migrations.RenameField(model_name='stockrecord', old_name='price_excl_tax', new_name='price', ),
        migrations.AlterField(
            model_name='partner',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='partneraddress',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='stockalert',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='stockrecord',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
