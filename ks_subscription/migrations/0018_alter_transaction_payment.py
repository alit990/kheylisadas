# Generated by Django 4.2.4 on 2023-10-30 13:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ks_subscription', '0017_alter_payment_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ks_subscription.payment'),
        ),
    ]
