# Generated by Django 4.2.4 on 2025-01-05 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ks_category', '0034_alter_category_is_disabled'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ccdetail',
            name='icon',
        ),
        migrations.RemoveField(
            model_name='chapter',
            name='icon',
        ),
        migrations.RemoveField(
            model_name='week',
            name='icon',
        ),
        migrations.AlterField(
            model_name='ccdetail',
            name='audio_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ccdetail',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
