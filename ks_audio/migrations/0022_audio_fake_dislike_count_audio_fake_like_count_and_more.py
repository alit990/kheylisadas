# Generated by Django 4.2.4 on 2023-11-21 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ks_audio', '0021_alter_audio_duration_alter_audioweek_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='audio',
            name='fake_dislike_count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='audio',
            name='fake_like_count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='audio',
            name='fake_played_count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='audiocourse',
            name='fake_dislike_count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='audiocourse',
            name='fake_like_count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='audiocourse',
            name='fake_played_count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='audioweek',
            name='fake_dislike_count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='audioweek',
            name='fake_like_count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='audioweek',
            name='fake_played_count',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
