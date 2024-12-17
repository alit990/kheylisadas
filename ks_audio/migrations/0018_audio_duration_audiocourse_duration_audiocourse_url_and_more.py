# Generated by Django 4.2.4 on 2023-11-07 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ks_audio', '0017_audio_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='audio',
            name='duration',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='audiocourse',
            name='duration',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='audiocourse',
            name='url',
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name='audioweek',
            name='duration',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='audioweek',
            name='url',
            field=models.URLField(null=True),
        ),
    ]
