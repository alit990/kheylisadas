from django.urls import path

from ks_audio.views import get_csrf_token, get_audio_url, AudioDetailView, add_audio_comment

urlpatterns = [

    path('get_csrf_token/', get_csrf_token, name='get_csrf_token'),
    path('get_audio_url/', get_audio_url, name='get_audio_url'),

    path('audio/<int:pk>/', AudioDetailView.as_view(), name='audio_detail'),
    path('add-audio-comment', add_audio_comment, name='add_audio_comment'),



]
