# Generated by Django 4.2.4 on 2023-09-16 15:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ks_audio', '0007_audio_ccdetail_audiocourse_course_audioweek_week'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='audio',
            name='ccdetail',
        ),
        migrations.RemoveField(
            model_name='audiocourse',
            name='course',
        ),
        migrations.RemoveField(
            model_name='audioweek',
            name='week',
        ),
    ]
