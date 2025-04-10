# Generated by Django 4.2.4 on 2025-01-06 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ks_category', '0036_alter_category_is_active_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ccdetail',
            name='level',
        ),
        migrations.RemoveField(
            model_name='week',
            name='level',
        ),
        migrations.AlterField(
            model_name='ccdetail',
            name='fake_dislike_count',
            field=models.IntegerField(default=4),
        ),
        migrations.AlterField(
            model_name='ccdetail',
            name='fake_like_count',
            field=models.IntegerField(default=8),
        ),
        migrations.AlterField(
            model_name='ccdetail',
            name='fake_visit_count',
            field=models.IntegerField(default=30),
        ),
    ]
