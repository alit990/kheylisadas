# Generated by Django 4.2.4 on 2023-11-08 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ks_audio', '0018_audio_duration_audiocourse_duration_audiocourse_url_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='audiocourse',
            name='duration_audio',
            field=models.DurationField(blank=True, null=True),
        ),
    ]
