# Generated by Django 4.2.4 on 2023-09-05 02:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ks_subscription', '0007_payment_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='in_process',
            field=models.BooleanField(default=False),
        ),
    ]
