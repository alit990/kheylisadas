# Generated by Django 4.2.4 on 2025-03-17 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ks_audio', '0055_alter_audio_fake_like_count_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audio',
            name='fake_dislike_count',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='audio',
            name='fake_played_count',
            field=models.IntegerField(default=11),
        ),
        migrations.AlterField(
            model_name='audio',
            name='fake_visit_count',
            field=models.IntegerField(default=10),
        ),
    ]
