# Generated by Django 4.2.4 on 2025-01-02 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ks_category', '0033_category_is_disabled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='is_disabled',
            field=models.BooleanField(default=True),
        ),
    ]
