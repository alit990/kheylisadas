from django.core.management.base import BaseCommand
import random
from datetime import timedelta

from ks_audio.models import Audio


class Command(BaseCommand):
    help = 'Update duration field for audios with empty duration'

    def handle(self, *args, **kwargs):
        audios = Audio.objects.filter(duration__isnull=True) | Audio.objects.filter(duration=timedelta(0))

        for audio in audios:
            minutes = random.randint(10, 30)
            seconds = random.randint(1, 59)
            random_duration = timedelta(minutes=minutes, seconds=seconds)
            audio.duration = random_duration
            audio.save()

        self.stdout.write(self.style.SUCCESS(f"Updated {audios.count()} records with random duration."))
