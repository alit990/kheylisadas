# Generated by Django 4.2.4 on 2023-10-27 10:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ks_audio', '0015_audio_is_lock'),
        ('ks_vote', '0006_alter_articlevote_user_alter_audiovote_user_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AudioWeekVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.IntegerField(blank=True, choices=[(1, 'Like'), (0, 'Dislike')], null=True)),
                ('ip', models.CharField(blank=True, max_length=30, null=True)),
                ('audio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ks_audio.audioweek')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AudioWeekPlaylist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('audio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ks_audio.audioweek')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AudioPlaylist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('audio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ks_audio.audio')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AudioCourseVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.IntegerField(blank=True, choices=[(1, 'Like'), (0, 'Dislike')], null=True)),
                ('ip', models.CharField(blank=True, max_length=30, null=True)),
                ('audio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ks_audio.audiocourse')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
