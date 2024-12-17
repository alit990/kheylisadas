# Generated by Django 4.2.4 on 2023-11-21 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ks_audio', '0023_alter_audio_fake_dislike_count_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audio',
            name='fake_dislike_count',
            field=models.IntegerField(default=5),
        ),
        migrations.AlterField(
            model_name='audio',
            name='fake_like_count',
            field=models.IntegerField(default=5),
        ),
        migrations.AlterField(
            model_name='audio',
            name='fake_played_count',
            field=models.IntegerField(default=5),
        ),
        migrations.AlterField(
            model_name='audiocourse',
            name='fake_dislike_count',
            field=models.IntegerField(default=5),
        ),
        migrations.AlterField(
            model_name='audiocourse',
            name='fake_like_count',
            field=models.IntegerField(default=5),
        ),
        migrations.AlterField(
            model_name='audiocourse',
            name='fake_played_count',
            field=models.IntegerField(default=5),
        ),
        migrations.AlterField(
            model_name='audioweek',
            name='fake_dislike_count',
            field=models.IntegerField(default=5),
        ),
        migrations.AlterField(
            model_name='audioweek',
            name='fake_like_count',
            field=models.IntegerField(default=5),
        ),
        migrations.AlterField(
            model_name='audioweek',
            name='fake_played_count',
            field=models.IntegerField(default=5),
        ),
    ]
