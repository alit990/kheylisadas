# Generated by Django 4.2.4 on 2023-11-21 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ks_course', '0020_alter_course_fake_dislike_count_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='fake_dislike_count',
            field=models.IntegerField(default=5),
        ),
        migrations.AlterField(
            model_name='course',
            name='fake_like_count',
            field=models.IntegerField(default=5),
        ),
        migrations.AlterField(
            model_name='course',
            name='fake_subscriber_count',
            field=models.IntegerField(default=25),
        ),
        migrations.AlterField(
            model_name='course',
            name='fake_visit_count',
            field=models.IntegerField(default=5),
        ),
    ]
