# Generated by Django 4.2.4 on 2024-02-12 12:09

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ks_subscription', '0023_rename_is_active_transaction_is_paid_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='description_rich',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True),
        ),
    ]
