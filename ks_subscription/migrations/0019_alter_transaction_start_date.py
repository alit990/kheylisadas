# Generated by Django 4.2.4 on 2023-10-30 13:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ks_subscription', '0018_alter_transaction_payment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='start_date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
    ]
