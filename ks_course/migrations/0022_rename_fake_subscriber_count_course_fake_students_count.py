# Generated by Django 4.2.4 on 2023-11-23 11:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ks_course', '0021_alter_course_fake_dislike_count_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='fake_subscriber_count',
            new_name='fake_students_count',
        ),
    ]
