# Generated by Django 4.2.4 on 2025-01-07 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ks_category', '0037_remove_ccdetail_level_remove_week_level_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ccdetail',
            name='fake_dislike_count',
            field=models.IntegerField(default=6),
        ),
        migrations.AlterField(
            model_name='ccdetail',
            name='fake_like_count',
            field=models.IntegerField(default=10),
        ),
        migrations.AlterField(
            model_name='ccdetail',
            name='fake_visit_count',
            field=models.IntegerField(default=27),
        ),
    ]
