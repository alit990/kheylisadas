# Generated by Django 4.2.4 on 2025-03-14 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ks_audio', '0052_alter_audio_fake_dislike_count_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audio',
            name='fake_like_count',
            field=models.IntegerField(default=17),
        ),
        migrations.AlterField(
            model_name='audio',
            name='fake_played_count',
            field=models.IntegerField(default=24),
        ),
        migrations.AlterField(
            model_name='audio',
            name='fake_visit_count',
            field=models.IntegerField(default=22),
        ),
    ]
