# Generated by Django 4.2.4 on 2023-08-25 02:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ks_tag', '0001_initial'),
        ('ks_category', '0010_ccdetail_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='ccdetail',
            name='tags',
            field=models.ManyToManyField(blank=True, to='ks_tag.tagccdetail'),
        ),
    ]
