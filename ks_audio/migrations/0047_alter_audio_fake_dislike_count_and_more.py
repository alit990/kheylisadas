# Generated by Django 4.2.4 on 2025-01-11 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ks_audio', '0046_alter_audio_fake_dislike_count_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audio',
            name='fake_dislike_count',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='audio',
            name='fake_like_count',
            field=models.IntegerField(default=19),
        ),
        migrations.AlterField(
            model_name='audio',
            name='fake_played_count',
            field=models.IntegerField(default=15),
        ),
        migrations.AlterField(
            model_name='audio',
            name='fake_visit_count',
            field=models.IntegerField(default=14),
        ),
    ]
