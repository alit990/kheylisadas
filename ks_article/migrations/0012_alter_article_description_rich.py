# Generated by Django 4.2.4 on 2023-12-17 12:10

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ks_article', '0011_article_description_rich'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='description_rich',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True),
        ),
    ]
