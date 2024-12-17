from django.urls import path
from ks_vote.views import set_article_vote, set_week_vote, set_audio_vote, set_course_vote, set_ccdetail_vote, \
    add_audio_to_playlist, set_audio_course_vote, set_audio_week_vote, add_week_audio_to_playlist, \
    set_audio_article_vote

urlpatterns = [
    path('set-article-vote', set_article_vote, name='set_article_vote'),
    path('set-week-vote', set_week_vote, name='set_week_vote'),
    path('set-course-vote', set_course_vote, name='set_course_vote'),
    path('set-ccdetail-vote', set_ccdetail_vote, name='set_ccdetail_vote'),
    path('add-audio-to-playlist', add_audio_to_playlist, name='add_audio_to_playlist'),
    path('add-week-audio-to-playlist', add_week_audio_to_playlist, name='add_week_audio_to_playlist'),
    path('set-audio-vote', set_audio_vote, name='set_audio_vote'),
    path('set-audio-course-vote', set_audio_course_vote, name='set_audio_course_vote'),
    path('set-audio-week-vote', set_audio_week_vote, name='set_audio_week_vote'),
    path('set-audio-article-vote', set_audio_article_vote, name='set_audio_article_vote'),
]


