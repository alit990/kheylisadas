# Generated by Django 4.2.4 on 2024-02-28 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ks_subscription', '0027_giftplan'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='off_price',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
