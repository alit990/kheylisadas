# Generated by Django 4.2.4 on 2023-09-04 07:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ks_subscription', '0004_payment_status_transaction_info'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='start_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
