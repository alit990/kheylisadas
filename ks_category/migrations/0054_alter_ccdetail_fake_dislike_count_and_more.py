# Generated by Django 4.2.4 on 2025-03-17 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ks_category', '0053_alter_ccdetail_fake_dislike_count_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ccdetail',
            name='fake_dislike_count',
            field=models.IntegerField(default=7),
        ),
        migrations.AlterField(
            model_name='ccdetail',
            name='fake_like_count',
            field=models.IntegerField(default=18),
        ),
        migrations.AlterField(
            model_name='ccdetail',
            name='fake_visit_count',
            field=models.IntegerField(default=17),
        ),
    ]
