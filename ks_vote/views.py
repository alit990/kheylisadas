from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ks_article.models import Article
from ks_audio.models import Audio, AudioCourse, AudioWeek, AudioArticle
from ks_category.models import Week, CCDetail
from ks_course.models import Course
from ks_vote.models import ArticleVote, WeekVote, CCDetailVote, CourseVote, AudioVote, AudioCourseVote, AudioWeekVote, \
    AudioPlaylist, AudioWeekPlaylist, AudioArticleVote
from utility.http_service import get_client_ip


# Create your views here.
def set_article_vote(request: HttpRequest):
    article_id = request.GET.get('article_id')
    vote = int(request.GET.get('vote'))
    print(article_id, vote)
    article = Article.objects.filter(id=article_id).first()
    user_ip = get_client_ip(request)
    user_id = None
    if request.user.is_authenticated:
        user_id = request.user.id
    if ArticleVote.objects.filter(article_id=article_id, user_id=user_id).exists():
        exist_vote: ArticleVote = ArticleVote.objects.filter(article_id=article_id, user_id=user_id).first()
        if vote == exist_vote.vote:
            return HttpResponse('no_need_to_change')
        elif vote == 1:
            exist_vote.vote = ArticleVote.LIKE
            exist_vote.save()
            context = {
                'article': article,
                'article_likes_count': ArticleVote.objects.filter(article_id=article.id, vote=1).count(),
                'article_dislikes_count': ArticleVote.objects.filter(article_id=article.id, vote=0).count(),
                'article_user_vote': vote
            }
            return render(request, 'vote/includes/article_vote_partial.html', context)
        elif vote == 0:
            exist_vote.vote = ArticleVote.DISLIKE
            exist_vote.save()
            context = {
                'article': article,
                'article_likes_count': ArticleVote.objects.filter(article_id=article.id, vote=1).count(),
                'article_dislikes_count': ArticleVote.objects.filter(article_id=article.id, vote=0).count(),
                'article_user_vote': vote
            }
            return render(request, 'vote/includes/article_vote_partial.html', context)
        return HttpResponse('exist_but_invalid')
    else:
        if vote == 1:
            new_vote = ArticleVote(article_id=article_id, user_id=user_id, vote=1, ip=user_ip)
            new_vote.save()
            context = {
                'article': article,
                'article_likes_count': ArticleVote.objects.filter(article_id=article.id, vote=1).count(),
                'article_dislikes_count': ArticleVote.objects.filter(article_id=article.id, vote=0).count(),
                'article_user_vote': vote
            }
            return render(request, 'vote/includes/article_vote_partial.html', context)
        elif vote == 0:
            new_vote = ArticleVote(article_id=article_id, user_id=user_id, vote=0, ip=user_ip)
            new_vote.save()
            context = {
                'article': article,
                'article_likes_count': ArticleVote.objects.filter(article_id=article.id, vote=1).count(),
                'article_dislikes_count': ArticleVote.objects.filter(article_id=article.id, vote=0).count(),
                'article_user_vote': vote
            }
            return render(request, 'vote/includes/article_vote_partial.html', context)
        return HttpResponse('not_exist_and_invalid')


def set_week_vote(request: HttpRequest):
    week_id = request.GET.get('week_id')
    vote = int(request.GET.get('vote'))
    print(week_id, vote)
    week = Week.objects.filter(id=week_id).first()
    user_ip = get_client_ip(request)
    user_id = None
    if request.user.is_authenticated:
        user_id = request.user.id
    if WeekVote.objects.filter(week_id=week_id, user_id=user_id).exists():
        exist_vote: WeekVote = WeekVote.objects.filter(week_id=week_id, user_id=user_id).first()
        if vote == exist_vote.vote:
            return HttpResponse('no_need_to_change')
        elif vote == 1:
            exist_vote.vote = 1
            exist_vote.save()
            context = {
                'week': week,
                'week_likes_count': WeekVote.objects.filter(week_id=week.id, vote=1).count(),
                'week_dislikes_count': WeekVote.objects.filter(week_id=week.id, vote=0).count(),
                'week_user_vote': vote
            }
            return render(request, 'vote/includes/week_vote_partial.html', context)
        elif vote == 0:
            exist_vote.vote = 0
            exist_vote.save()
            context = {
                'week': week,
                'week_likes_count': WeekVote.objects.filter(week_id=week.id, vote=1).count(),
                'week_dislikes_count': WeekVote.objects.filter(week_id=week.id, vote=0).count(),
                'week_user_vote': vote
            }
            return render(request, 'vote/includes/week_vote_partial.html', context)
        return HttpResponse('exist_but_invalid')
    else:
        if vote == 1:
            new_vote = WeekVote(week_id=week_id, user_id=user_id, vote=1, ip=user_ip)
            new_vote.save()
            context = {
                'week': week,
                'week_likes_count': WeekVote.objects.filter(week_id=week.id, vote=1).count(),
                'week_dislikes_count': WeekVote.objects.filter(week_id=week.id, vote=0).count(),
                'week_user_vote': vote
            }
            return render(request, 'vote/includes/week_vote_partial.html', context)
        elif vote == 0:
            new_vote = WeekVote(week_id=week_id, user_id=user_id, vote=0, ip=user_ip)
            new_vote.save()
            context = {
                'week': week,
                'week_likes_count': WeekVote.objects.filter(week_id=week.id, vote=1).count(),
                'week_dislikes_count': WeekVote.objects.filter(week_id=week.id, vote=0).count(),
                'week_user_vote': vote
            }
            return render(request, 'vote/includes/week_vote_partial.html', context)
        return HttpResponse('not_exist_and_invalid')


def set_ccdetail_vote(request: HttpRequest):
    ccdetail_id = request.GET.get('ccdetail_id')
    vote = int(request.GET.get('vote'))
    ccdetail = CCDetail.objects.filter(id=ccdetail_id).first()
    user_ip = get_client_ip(request)
    user_id = None
    if request.user.is_authenticated:
        user_id = request.user.id
    if CCDetailVote.objects.filter(ccdetail_id=ccdetail_id, user_id=user_id).exists():
        exist_vote: CCDetailVote = CCDetailVote.objects.filter(ccdetail_id=ccdetail_id, user_id=user_id).first()
        if vote == exist_vote.vote:
            return HttpResponse('no_need_to_change')
        elif vote == 1:
            exist_vote.vote = 1
            exist_vote.save()
            context = {
                'ccdetail': ccdetail,
                'ccdetail_likes_count': CCDetailVote.objects.filter(ccdetail_id=ccdetail.id, vote=1).count(),
                'ccdetail_dislikes_count': CCDetailVote.objects.filter(ccdetail_id=ccdetail.id, vote=0).count(),
                'ccdetail_user_vote': vote
            }
            return render(request, 'vote/includes/ccdetail_vote_partial.html', context)
        elif vote == 0:
            exist_vote.vote = 0
            exist_vote.save()
            context = {
                'ccdetail': ccdetail,
                'ccdetail_likes_count': CCDetailVote.objects.filter(ccdetail_id=ccdetail.id, vote=1).count(),
                'ccdetail_dislikes_count': CCDetailVote.objects.filter(ccdetail_id=ccdetail.id, vote=0).count(),
                'ccdetail_user_vote': vote
            }
            return render(request, 'vote/includes/ccdetail_vote_partial.html', context)
        return HttpResponse('exist_but_invalid')
    else:
        if vote == 1:
            new_vote = CCDetailVote(ccdetail_id=ccdetail_id, user_id=user_id, vote=1, ip=user_ip)
            new_vote.save()
            context = {
                'ccdetail': ccdetail,
                'ccdetail_likes_count': CCDetailVote.objects.filter(ccdetail_id=ccdetail.id, vote=1).count(),
                'ccdetail_dislikes_count': CCDetailVote.objects.filter(ccdetail_id=ccdetail.id, vote=0).count(),
                'ccdetail_user_vote': vote
            }
            return render(request, 'vote/includes/ccdetail_vote_partial.html', context)
        elif vote == 0:
            new_vote = CCDetailVote(ccdetail_id=ccdetail_id, user_id=user_id, vote=0, ip=user_ip)
            new_vote.save()
            context = {
                'ccdetail': ccdetail,
                'ccdetail_likes_count': CCDetailVote.objects.filter(ccdetail_id=ccdetail.id, vote=1).count(),
                'ccdetail_dislikes_count': CCDetailVote.objects.filter(ccdetail_id=ccdetail.id, vote=0).count(),
                'ccdetail_user_vote': vote
            }
            return render(request, 'vote/includes/ccdetail_vote_partial.html', context)
        return HttpResponse('not_exist_and_invalid')


def set_course_vote(request: HttpRequest):
    course_id = request.GET.get('course_id')
    vote = int(request.GET.get('vote'))
    print(course_id, vote)
    course = Course.objects.filter(id=course_id).first()
    user_ip = get_client_ip(request)
    user_id = None
    if request.user.is_authenticated:
        user_id = request.user.id
    if CourseVote.objects.filter(course_id=course_id, user_id=user_id).exists():
        exist_vote: CourseVote = CourseVote.objects.filter(course_id=course_id, user_id=user_id).first()
        if vote == exist_vote.vote:
            return HttpResponse('no_need_to_change')
        elif vote == 1:
            exist_vote.vote = 1
            exist_vote.save()
            context = {
                'course': course,
                'course_likes_count': CourseVote.objects.filter(course_id=course.id, vote=1).count(),
                'course_dislikes_count': CourseVote.objects.filter(course_id=course.id, vote=0).count(),
                'course_user_vote': vote
            }
            return render(request, 'vote/includes/course_vote_partial.html', context)
        elif vote == 0:
            exist_vote.vote = 0
            exist_vote.save()
            context = {
                'course': course,
                'course_likes_count': CourseVote.objects.filter(course_id=course.id, vote=1).count(),
                'course_dislikes_count': CourseVote.objects.filter(course_id=course.id, vote=0).count(),
                'course_user_vote': vote
            }
            return render(request, 'vote/includes/course_vote_partial.html', context)
        return HttpResponse('exist_but_invalid')
    else:
        if vote == 1:
            new_vote = CourseVote(course_id=course_id, user_id=user_id, vote=1, ip=user_ip)
            new_vote.save()
            context = {
                'course': course,
                'course_likes_count': CourseVote.objects.filter(course_id=course.id, vote=1).count(),
                'course_dislikes_count': CourseVote.objects.filter(course_id=course.id, vote=0).count(),
                'course_user_vote': vote
            }
            return render(request, 'vote/includes/course_vote_partial.html', context)
        elif vote == 0:
            new_vote = CourseVote(course_id=course_id, user_id=user_id, vote=0, ip=user_ip)
            new_vote.save()
            context = {
                'course': course,
                'course_likes_count': CourseVote.objects.filter(course_id=course.id, vote=1).count(),
                'course_dislikes_count': CourseVote.objects.filter(course_id=course.id, vote=0).count(),
                'course_user_vote': vote
            }
            return render(request, 'vote/includes/course_vote_partial.html', context)
        return HttpResponse('not_exist_and_invalid')


def set_audio_vote(request: HttpRequest):
    audio_id = request.GET.get('audio_id')
    vote = int(request.GET.get('vote'))
    audio = Audio.objects.filter(id=audio_id).first()
    user_ip = get_client_ip(request)
    user_id = None
    added_playlist = "False"
    if request.user.is_authenticated:
        user_id = request.user.id
        if AudioPlaylist.objects.filter(user_id=user_id, audio_id=audio_id, is_delete=False).exists():
            added_playlist = "True"
    if AudioVote.objects.filter(audio_id=audio_id, user_id=user_id).exists():
        exist_vote: AudioVote = AudioVote.objects.filter(audio_id=audio_id, user_id=user_id).first()
        if vote == exist_vote.vote:
            return HttpResponse('no_need_to_change')
        elif vote == 1:
            exist_vote.vote = 1
            exist_vote.save()
            context = {
                'audio': audio,
                'like_count': AudioVote.objects.filter(audio_id=audio.id, vote=1).count(),
                'dislike_count': AudioVote.objects.filter(audio_id=audio.id, vote=0).count(),
                'user_vote': vote,
                'added_playlist': added_playlist
            }
            return render(request, 'vote/includes/audio_vote_partial.html', context)
        elif vote == 0:
            exist_vote.vote = 0
            exist_vote.save()
            context = {
                'audio': audio,
                'like_count': AudioVote.objects.filter(audio_id=audio.id, vote=1).count(),
                'dislike_count': AudioVote.objects.filter(audio_id=audio.id, vote=0).count(),
                'user_vote': vote,
                'added_playlist': added_playlist
            }
            return render(request, 'vote/includes/audio_vote_partial.html', context)
        return HttpResponse('exist_but_invalid')
    else:
        if vote == 1:
            new_vote = AudioVote(audio_id=audio_id, user_id=user_id, vote=1, ip=user_ip)
            new_vote.save()
            context = {
                'audio': audio,
                'like_count': AudioVote.objects.filter(audio_id=audio.id, vote=1).count(),
                'dislike_count': AudioVote.objects.filter(audio_id=audio.id, vote=0).count(),
                'user_vote': vote,
                'added_playlist': added_playlist
            }
            return render(request, 'vote/includes/audio_vote_partial.html', context)
        elif vote == 0:
            new_vote = AudioVote(audio_id=audio_id, user_id=user_id, vote=0, ip=user_ip)
            new_vote.save()
            context = {
                'audio': audio,
                'like_count': AudioVote.objects.filter(audio_id=audio.id, vote=1).count(),
                'dislike_count': AudioVote.objects.filter(audio_id=audio.id, vote=0).count(),
                'user_vote': vote,
                'added_playlist': added_playlist
            }
            return render(request, 'vote/includes/audio_vote_partial.html', context)
        return HttpResponse('not_exist_and_invalid')


def set_audio_course_vote(request: HttpRequest):
    audio_id = request.GET.get('audio_id')
    vote = int(request.GET.get('vote'))
    print(audio_id, vote)
    audio = AudioCourse.objects.filter(id=audio_id).first()
    user_ip = get_client_ip(request)
    user_id = None
    if request.user.is_authenticated:
        user_id = request.user.id
    if AudioCourseVote.objects.filter(audio_id=audio_id, user_id=user_id).exists():
        exist_vote: AudioCourseVote = AudioCourseVote.objects.filter(audio_id=audio_id, user_id=user_id).first()
        if vote == exist_vote.vote:
            return HttpResponse('no_need_to_change')
        elif vote == 1:
            exist_vote.vote = 1
            exist_vote.save()
            context = {
                'audio': audio,
                'like_count': AudioCourseVote.objects.filter(audio_id=audio.id, vote=1).count(),
                'dislike_count': AudioCourseVote.objects.filter(audio_id=audio.id, vote=0).count(),
                'user_vote': vote,
                'page': 'COURSE'
            }
            return render(request, 'vote/includes/audio_vote_partial.html', context)
        elif vote == 0:
            exist_vote.vote = 0
            exist_vote.save()
            context = {
                'audio': audio,
                'like_count': AudioCourseVote.objects.filter(audio_id=audio.id, vote=1).count(),
                'dislike_count': AudioCourseVote.objects.filter(audio_id=audio.id, vote=0).count(),
                'user_vote': vote,
                'page': 'COURSE'
            }
            return render(request, 'vote/includes/audio_vote_partial.html', context)
        return HttpResponse('exist_but_invalid')
    else:
        if vote == 1:
            new_vote = AudioCourseVote(audio_id=audio_id, user_id=user_id, vote=1, ip=user_ip)
            new_vote.save()
            context = {
                'audio': audio,
                'like_count': AudioCourseVote.objects.filter(audio_id=audio.id, vote=1).count(),
                'dislike_count': AudioCourseVote.objects.filter(audio_id=audio.id, vote=0).count(),
                'user_vote': vote,
                'page': 'COURSE'
            }
            return render(request, 'vote/includes/audio_vote_partial.html', context)
        elif vote == 0:
            new_vote = AudioCourseVote(audio_id=audio_id, user_id=user_id, vote=0, ip=user_ip)
            new_vote.save()
            context = {
                'audio': audio,
                'like_count': AudioCourseVote.objects.filter(audio_id=audio.id, vote=1).count(),
                'dislike_count': AudioCourseVote.objects.filter(audio_id=audio.id, vote=0).count(),
                'user_vote': vote,
                'page': 'COURSE'
            }
            return render(request, 'vote/includes/audio_vote_partial.html', context)
        return HttpResponse('not_exist_and_invalid')


def set_audio_week_vote(request: HttpRequest):
    audio_id = request.GET.get('audio_id')
    vote = int(request.GET.get('vote'))
    print(audio_id, vote)
    audio = AudioWeek.objects.filter(id=audio_id).first()
    user_ip = get_client_ip(request)
    user_id = None
    added_playlist = "False"
    if request.user.is_authenticated:
        user_id = request.user.id
        if AudioWeekPlaylist.objects.filter(user_id=user_id, audio_id=audio_id, is_delete=False).exists():
            added_playlist = "True"
    if AudioWeekVote.objects.filter(audio_id=audio_id, user_id=user_id).exists():
        exist_vote: AudioWeekVote = AudioWeekVote.objects.filter(audio_id=audio_id, user_id=user_id).first()
        if vote == exist_vote.vote:
            return HttpResponse('no_need_to_change')
        elif vote == 1:
            exist_vote.vote = 1
            exist_vote.save()
            context = {
                'audio': audio,
                'like_count': AudioWeekVote.objects.filter(audio_id=audio.id, vote=1).count(),
                'dislike_count': AudioWeekVote.objects.filter(audio_id=audio.id, vote=0).count(),
                'user_vote': vote,
                'added_playlist': added_playlist,
                'page': 'WEEK'
            }
            return render(request, 'vote/includes/audio_vote_partial.html', context)
        elif vote == 0:
            exist_vote.vote = 0
            exist_vote.save()
            context = {
                'audio': audio,
                'like_count': AudioWeekVote.objects.filter(audio_id=audio.id, vote=1).count(),
                'dislike_count': AudioWeekVote.objects.filter(audio_id=audio.id, vote=0).count(),
                'user_vote': vote,
                'added_playlist': added_playlist,
                'page': 'WEEK'
            }
            return render(request, 'vote/includes/audio_vote_partial.html', context)
        return HttpResponse('exist_but_invalid')
    else:
        if vote == 1:
            new_vote = AudioWeekVote(audio_id=audio_id, user_id=user_id, vote=1, ip=user_ip)
            new_vote.save()
            context = {
                'audio': audio,
                'like_count': AudioWeekVote.objects.filter(audio_id=audio.id, vote=1).count(),
                'dislike_count': AudioWeekVote.objects.filter(audio_id=audio.id, vote=0).count(),
                'user_vote': vote,
                'added_playlist': added_playlist,
                'page': 'WEEK'
            }
            return render(request, 'vote/includes/audio_vote_partial.html', context)
        elif vote == 0:
            new_vote = AudioWeekVote(audio_id=audio_id, user_id=user_id, vote=0, ip=user_ip)
            new_vote.save()
            context = {
                'audio': audio,
                'like_count': AudioWeekVote.objects.filter(audio_id=audio.id, vote=1).count(),
                'dislike_count': AudioWeekVote.objects.filter(audio_id=audio.id, vote=0).count(),
                'user_vote': vote,
                'added_playlist': added_playlist,
                'page': 'WEEK'
            }
            return render(request, 'vote/includes/audio_vote_partial.html', context)
        return HttpResponse('not_exist_and_invalid')

def set_audio_article_vote(request: HttpRequest):
    audio_id = request.GET.get('audio_id')
    vote = int(request.GET.get('vote'))
    print(audio_id, vote)
    audio = AudioArticle.objects.filter(id=audio_id).first()
    user_ip = get_client_ip(request)
    user_id = None
    added_playlist = "False"
    if request.user.is_authenticated:
        user_id = request.user.id
    if AudioArticleVote.objects.filter(audio_id=audio_id, user_id=user_id).exists():
        exist_vote: AudioArticleVote = AudioArticleVote.objects.filter(audio_id=audio_id, user_id=user_id).first()
        if vote == exist_vote.vote:
            return HttpResponse('no_need_to_change')
        elif vote == 1:
            exist_vote.vote = 1
            exist_vote.save()
            context = {
                'audio': audio,
                'like_count': AudioArticleVote.objects.filter(audio_id=audio.id, vote=1).count(),
                'dislike_count': AudioArticleVote.objects.filter(audio_id=audio.id, vote=0).count(),
                'user_vote': vote,
                'added_playlist': added_playlist,
                'page': 'ARTICLE'
            }
            return render(request, 'vote/includes/audio_vote_partial.html', context)
        elif vote == 0:
            exist_vote.vote = 0
            exist_vote.save()
            context = {
                'audio': audio,
                'like_count': AudioArticleVote.objects.filter(audio_id=audio.id, vote=1).count(),
                'dislike_count': AudioArticleVote.objects.filter(audio_id=audio.id, vote=0).count(),
                'user_vote': vote,
                'added_playlist': added_playlist,
                'page': 'ARTICLE'
            }
            return render(request, 'vote/includes/audio_vote_partial.html', context)
        return HttpResponse('exist_but_invalid')
    else:
        if vote == 1:
            new_vote = AudioArticleVote(audio_id=audio_id, user_id=user_id, vote=1, ip=user_ip)
            new_vote.save()
            context = {
                'audio': audio,
                'like_count': AudioArticleVote.objects.filter(audio_id=audio.id, vote=1).count(),
                'dislike_count': AudioArticleVote.objects.filter(audio_id=audio.id, vote=0).count(),
                'user_vote': vote,
                'added_playlist': added_playlist,
                'page': 'ARTICLE'
            }
            return render(request, 'vote/includes/audio_vote_partial.html', context)
        elif vote == 0:
            new_vote = AudioArticleVote(audio_id=audio_id, user_id=user_id, vote=0, ip=user_ip)
            new_vote.save()
            context = {
                'audio': audio,
                'like_count': AudioArticleVote.objects.filter(audio_id=audio.id, vote=1).count(),
                'dislike_count': AudioArticleVote.objects.filter(audio_id=audio.id, vote=0).count(),
                'user_vote': vote,
                'added_playlist': added_playlist,
                'page': 'ARTICLE'
            }
            return render(request, 'vote/includes/audio_vote_partial.html', context)
        return HttpResponse('not_exist_and_invalid')



def add_audio_to_playlist(request: HttpRequest):
    audio_id = request.GET.get('audio_id')
    audio = Audio.objects.filter(id=audio_id).first()
    user_id = None
    if request.user.is_authenticated:  # this is done because user authenticated is necessary
        user_id = request.user.id
    audio_playlist, created = AudioPlaylist.objects.get_or_create(user_id=user_id, audio_id=audio_id)
    if created:
        audio_playlist.save()
        context = {
            'audio': audio,
            'added_playlist': "True"
        }
    else:
        if audio_playlist.is_delete:
            audio_playlist.is_delete = False
            audio_playlist.save()
            context = {
                'audio': audio,
                'added_playlist': "True"
            }
        else:
            audio_playlist.is_delete = True
            audio_playlist.save()
            context = {
                'audio': audio,
                'added_playlist': "False"
            }
    return render(request, 'vote/includes/audio_playlist_button_partial.html', context)


def add_week_audio_to_playlist(request: HttpRequest):
    audio_id = request.GET.get('audio_id')
    audio = Audio.objects.filter(id=audio_id).first()
    user_id = None
    if request.user.is_authenticated:  # this is done because user authenticated is necessary
        user_id = request.user.id
    audio_playlist, created = AudioWeekPlaylist.objects.get_or_create(user_id=user_id, audio_id=audio_id)
    if created:
        audio_playlist.save()
        context = {
            'audio': audio,
            'added_playlist': "True"
        }
    else:
        if audio_playlist.is_delete:
            audio_playlist.is_delete = False
            audio_playlist.save()
            context = {
                'audio': audio,
                'added_playlist': "True"
            }
        else:
            audio_playlist.is_delete = True
            audio_playlist.save()
            context = {
                'audio': audio,
                'added_playlist': "False"
            }
    return render(request, 'vote/includes/audio_playlist_button_partial.html', context)
