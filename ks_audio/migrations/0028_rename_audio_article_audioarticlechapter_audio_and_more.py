# Generated by Django 4.2.4 on 2023-12-18 18:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ks_audio', '0027_audioarticlechapter'),
    ]

    operations = [
        migrations.RenameField(
            model_name='audioarticlechapter',
            old_name='audio_article',
            new_name='audio',
        ),
        migrations.RenameField(
            model_name='audiocoursechapter',
            old_name='audio_course',
            new_name='audio',
        ),
        migrations.RenameField(
            model_name='audioweekchapter',
            old_name='audio_week',
            new_name='audio',
        ),
    ]
