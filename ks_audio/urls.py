from django.urls import path

from ks_audio.views import get_csrf_token, get_audio_url

urlpatterns = [
    path('get_csrf_token/', get_csrf_token, name='get_csrf_token'),
    path('get_audio_url/', get_audio_url, name='get_audio_url'),

]
