# Generated by Django 4.2.4 on 2025-01-12 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ks_audio', '0047_alter_audio_fake_dislike_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='audio',
            name='demo_url',
            field=models.CharField(blank=True, max_length=2083, null=True),
        ),
        migrations.AlterField(
            model_name='audio',
            name='fake_like_count',
            field=models.IntegerField(default=10),
        ),
        migrations.AlterField(
            model_name='audio',
            name='fake_played_count',
            field=models.IntegerField(default=24),
        ),
        migrations.AlterField(
            model_name='audio',
            name='fake_visit_count',
            field=models.IntegerField(default=18),
        ),
        migrations.AlterField(
            model_name='audiochapter',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
