# Generated by Django 2.0.6 on 2018-06-04 04:51

from django.db import migrations
import djstripe.fields


class Migration(migrations.Migration):

    dependencies = [
        ('djstripe', '0028_auto_20180604_0609'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='hosted_invoice_url',
            field=djstripe.fields.StripeCharField(help_text='The URL for the hosted invoice page, which allows customers to view and pay an invoice. If the invoice has not been frozen yet, this will be null.', max_length=799, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='invoice_pdf',
            field=djstripe.fields.StripeCharField(help_text='The link to download the PDF for the invoice. If the invoice has not been frozen yet, this will be null.', max_length=799, null=True),
        ),
    ]
