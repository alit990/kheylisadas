# Generated by Django 4.2.4 on 2024-12-23 19:56

from django.db import migrations
import django_ckeditor_5.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ks_article', '0016_remove_articlecategory_thumb'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='description_rich',
            field=django_ckeditor_5.fields.CKEditor5Field(blank=True, null=True, verbose_name='Description'),
        ),
    ]
