import json

from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.db.models import Q
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.views.generic import DetailView
from datetime import datetime, timedelta
from ks_account.models import User
from ks_audio.models import Audio, AudioWeek, AudioCourse, AudioArticle, AudioVisit, AudioChapter, FileAttachment, \
    VideoAttachment
from django.http import JsonResponse, HttpRequest, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt

from ks_category.models import AudioComment, CCDetail, Category
from ks_site.models import Avatar, SiteSetting
from ks_subscription.models import Transaction
from ks_vote.models import AudioVote, AudioPlaylist
from utility.context_chapter_preparation import MyChapter, MyChapterData
from utility.http_service import get_client_ip
from utility.utils import group_subscription_name, codename_audio_perm, codename_audio_week_perm


class AudioDetailView(DetailView):
    model = Audio
    template_name = 'audio_detail.html'  # نام قالبی که استفاده می‌کنید
    context_object_name = 'audio'  # نام شیء برای استفاده در قالب

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        has_perm = False
        audio = self.object
        has_audio = True if audio.url else False
        context['has_audio'] = has_audio
        chapter_index = self.request.GET.get('chapter', 0)  # مقدار پیش‌فرض 0 برای زمانی که پارامتر chapter موجود نباشد
        context['chapter_index'] = chapter_index  # اضافه کردن chapter_index به context
        audio.url = ""
        if audio.section.ccdetail.category.is_disabled:
            raise Http404("Category is disabled")
        if audio.is_lock:
            audio.is_lock = "True"
        else:
            audio.is_lock = "False"
        context['audio'] = audio
        same_section_audios = Audio.objects.filter(section=audio.section, is_active=True).exclude(id=audio.id)
        context['same_section_audios'] = same_section_audios
        #  برای سر فصل های دیگر این سن
        section = audio.section
        if not section.is_active:
            raise Http404
        ccdetail = section.ccdetail
        if not ccdetail.is_active:
            raise Http404
        chapter = ccdetail.chapter
        if not chapter.is_active:
            raise Http404
        category = ccdetail.category
        if not category.is_active:
            raise Http404
        ccdetails = CCDetail.objects.filter(category=category, is_active=True)
        my_chapters = []
        for ccdetail in ccdetails:
            chapter = ccdetail.chapter
            my_chapter = MyChapter(id=chapter.id, title=chapter.title, name=chapter.name, slug=chapter.slug,
                                   audio_url=ccdetail.audio_url, audio_count=ccdetail.audio_count)
            my_chapters.append(my_chapter)
        my_chapter_data = MyChapterData('chapter_data')
        my_chapter_data.add_chapter("chapters", my_chapters)
        data_js = str(my_chapter_data).replace("\'", "\"")
        data = json.loads(data_js)

        context['data'] = data
        context['category'] = category
        context['chapter'] = chapter
        context['ccdetails'] = ccdetails
        comments = AudioComment.objects.filter(audio_id=audio.id, parent=None,
                                               is_allowed=True).order_by('-create_date').prefetch_related(
            'audiocomment_set')
        comments_count = AudioComment.objects.filter(audio_id=audio.id, is_allowed=True).count()
        tags = audio.tags.filter(is_active=True)
        user_ip = get_client_ip(self.request)
        user_id = None
        if self.request.user.is_authenticated:
            user_id = self.request.user.id
            current_user: User = User.objects.filter(id=user_id, is_active=True).first()
            if AudioPlaylist.objects.filter(user_id=user_id, audio_id=audio.id).exists():
                added = AudioPlaylist.objects.filter(user_id=user_id, audio_id=audio.id).first()
                if added.is_delete:
                    context['added_playlist'] = False
                else:
                    context['added_playlist'] = True
            else:
                context['added_playlist'] = False

            # permission group for subscription
            has_perm = False
            has_subscription_group = current_user.groups.filter(name=group_subscription_name()).exists()
            if has_subscription_group:
                has_transaction = Transaction.objects.filter(user_id=current_user.id, is_paid=True,
                                                             is_expired=False).exists()
                if has_transaction:
                    transaction = Transaction.objects.filter(
                        user_id=current_user.id, is_paid=True, is_expired=False).first()
                    if transaction.is_expired_this:
                        content_type_audio = ContentType.objects.get_for_model(Audio)
                        perm_view_audio, created = Permission.objects.get_or_create(codename=codename_audio_perm(),
                                                                                    content_type=content_type_audio)
                        content_type_audio_week = ContentType.objects.get_for_model(AudioWeek)
                        perm_view_audio_week, created = Permission.objects.get_or_create(
                            codename=codename_audio_week_perm(),
                            content_type=content_type_audio_week)
                        plan_group, plan_created = Group.objects.get_or_create(name=group_subscription_name())
                        if plan_created:
                            plan_group.permissions.add(perm_view_audio, perm_view_audio_week)
                        current_user.groups.remove(plan_group)
                    else:
                        has_perm = True

            # has_perm = current_user.groups.filter(name=group_subscription_name()).exists()
            # print("has perm?", has_perm)
            # if Transaction.objects.filter(user_id=current_user.id, is_paid=True,
            #                               is_expired=False).exists() and has_perm:
            #     transaction: Transaction = Transaction.objects.filter(
            #         user_id=current_user.id, is_paid=True, is_expired=False).first()
            #     if transaction.is_expired_this:
            #         content_type_audio = ContentType.objects.get_for_model(Audio)
            #         perm_view_audio, created = Permission.objects.get_or_create(codename=codename_audio_perm(),
            #                                                                     content_type=content_type_audio)
            #         content_type_audio_week = ContentType.objects.get_for_model(AudioWeek)
            #         perm_view_audio_week, created = Permission.objects.get_or_create(
            #             codename=codename_audio_week_perm(),
            #             content_type=content_type_audio_week)
            #         plan_group, plan_created = Group.objects.get_or_create(name=group_subscription_name())
            #         if plan_created:
            #             plan_group.permissions.add(perm_view_audio, perm_view_audio_week)
            #         current_user.groups.remove(plan_group)
            #         has_perm = False
        has_been_visited = AudioVisit.objects.filter(ip__iexact=user_ip, audio_id=audio.id).exists()
        if not has_been_visited:
            new_visit = AudioVisit(ip=user_ip, user_id=user_id, audio_id=audio.id)
            new_visit.save()
        context['has_perm'] = has_perm
        context['comments'] = comments
        context['comments_count'] = comments_count
        context['tags'] = tags
        context['audio_likes_count'] = AudioVote.objects.filter(audio_id=audio.id, vote=1).count()
        context['audio_dislikes_count'] = AudioVote.objects.filter(audio_id=audio.id, vote=0).count()
        context['audio_user_vote'] = -1

        if AudioVote.objects.filter(audio_id=audio.id, user_id=user_id).exists():
            context['audio_user_vote'] = AudioVote.objects.filter(audio_id=audio.id,
                                                                  user_id=user_id).first().vote
        avatar = Avatar.objects.filter(is_main=True).first()
        context['avatar'] = avatar
        like_count = AudioVote.objects.filter(audio_id=audio.id, vote=1).count()
        dislike_count = AudioVote.objects.filter(audio_id=audio.id, vote=0).count()
        user_vote = -1
        if self.request.user.is_authenticated:
            if AudioVote.objects.filter(audio_id=audio.id, user_id=user_id).exists():
                user_vote = AudioVote.objects.filter(audio_id=audio.id, user_id=user_id).first().vote
        else:
            if AudioVote.objects.filter(audio_id=audio.id, ip=user_ip).exists():
                user_vote = AudioVote.objects.filter(audio_id=audio.id, ip=user_ip).first().vote

        # if audio.is_lock and not has_perm:
        #     a = Au(id=audio.id, title=audio.title, name=audio.name,
        #            description=audio.description, is_lock=audio.is_lock)
        # else:
        #     a = Au(id=audio.id, title=audio.title, name=audio.name,
        #            description=audio.description, is_lock=audio.is_lock, type=audio.type,
        #            like_count=like_count, dislike_count=dislike_count,
        #            fake_like_count=audio.fake_like_count, fake_dislike_count=audio.fake_dislike_count,
        #            user_vote=user_vote, added_playlist=added_playlist)
        chapter_set = AudioChapter.objects.filter(audio_id=audio.id,
                                                  is_active=True).order_by('start_time_seconds')
        context['like_count'] = like_count
        context['dislike_count'] = dislike_count
        context['user_vote'] = user_vote
        context['chapter_set'] = chapter_set
        audio_data = serializers.serialize('json', [audio])
        audio_json = json.loads(audio_data)[0]['fields']
        audio_json['id'] = audio.id
        context['audio_json'] = json.dumps(audio_json)
        chapters_data = serializers.serialize('json', chapter_set)
        chapters_json = []
        for chapter in json.loads(chapters_data):
            chapter_fields = chapter['fields']
            chapter_fields['id'] = chapter['pk']
            chapters_json.append(chapter_fields)
        context['chapters_json'] = json.dumps(chapters_json)
        if FileAttachment.objects.filter(audio=audio).exists():
            file = FileAttachment.objects.filter(audio=audio).first()
            has_file = True
            context['file'] = file
        else:
            has_file = False
        context['has_file'] = has_file
        if VideoAttachment.objects.filter(audio=audio).exists():
            video = VideoAttachment.objects.filter(audio=audio).first()
            has_video = True
            context['video'] = video
        else:
            has_video = False
        context['has_video'] = has_video
        site_setting = SiteSetting.objects.filter(is_main_setting=True).first()
        context['site_setting'] = site_setting
        categories = Category.objects.all()
        context['categories'] = categories
        return context


def add_audio_comment(request: HttpRequest):
    if request.user.is_authenticated:
        current_user = request.user
        audio_id = request.GET.get('audio_id')
        audio_comment = request.GET.get('audio_comment')
        parent_id = request.GET.get('parent_id')
        if request.user.is_staff:
            new_comment = AudioComment(audio_id=audio_id, text=audio_comment, user_id=request.user.id,
                                       parent_id=parent_id, is_allowed=True)
            new_comment.save()
            context = {
                'comments': AudioComment.objects.filter(audio_id=audio_id, parent=None,
                                                        is_allowed=True).order_by(
                    '-create_date').prefetch_related('audiocomment_set'),
                'comments_count': AudioComment.objects.filter(audio_id=audio_id, is_allowed=True).count()
            }
            return render(request, 'includes/comments_partial.html', context)
        else:
            limit_minutes_ago = datetime.now() - timedelta(minutes=5)
            comment_count_in_last_limit_min = AudioComment.objects.filter(
                Q(create_date__gte=limit_minutes_ago) & Q(user=current_user)).count()
            if comment_count_in_last_limit_min < 3:
                new_comment = AudioComment(audio_id=audio_id, text=audio_comment, user_id=request.user.id,
                                           parent_id=parent_id)
                new_comment.save()
                return HttpResponse('no-staff')
            else:
                return HttpResponse('too-many-comment')
    return HttpResponse('response')


def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})


@csrf_exempt
def get_audio_url(request):
    if request.method == 'POST':
        http_x_csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
        cookie_csrf_token = request.COOKIES.get('csrftoken', '')
        print(http_x_csrf_token)
        print(cookie_csrf_token)
        if http_x_csrf_token == cookie_csrf_token:
            audio_id = int(request.POST.get('audio_id'))
            audio_type = request.POST.get('audio_type')
            has_perm = request.POST.get('has_perm')
            if audio_type == "CCDETAIL":
                try:
                    audio_file = Audio.objects.get(id=audio_id)
                    if not audio_file.is_lock:
                        return JsonResponse({'url': audio_file.url})
                    else:
                        if has_perm:
                            return JsonResponse({'url': audio_file.url})
                        return JsonResponse({'error': 'File is locked'}, status=403)
                except Audio.DoesNotExist:
                    return JsonResponse({'error': 'File not found'}, status=404)
            elif audio_type == "WEEK":
                try:
                    audio_file = AudioWeek.objects.get(id=audio_id)
                    if not audio_file.is_lock:
                        audio_url = audio_file.url
                        return JsonResponse({'url': audio_url})
                    else:
                        return JsonResponse({'error': 'File is locked'}, status=403)
                except AudioWeek.DoesNotExist:
                    return JsonResponse({'error': 'File not found'}, status=404)
            elif audio_type == "COURSE":
                try:
                    audio_file = AudioCourse.objects.get(id=audio_id)
                    if not audio_file.is_lock:
                        audio_url = audio_file.url
                        return JsonResponse({'url': audio_url})
                    else:
                        return JsonResponse({'error': 'File is locked'}, status=403)
                except AudioCourse.DoesNotExist:
                    return JsonResponse({'error': 'File not found'}, status=404)
            elif audio_type == "ARTICLE":
                try:
                    audio_file = AudioArticle.objects.get(id=audio_id)
                    if not audio_file.is_lock:
                        audio_url = audio_file.url
                        return JsonResponse({'url': audio_url})
                    else:
                        return JsonResponse({'error': 'File is locked'}, status=403)
                except AudioArticle.DoesNotExist:
                    return JsonResponse({'error': 'File not found'}, status=404)
            else:
                pass

        else:
            return JsonResponse({'error': 'Invalid CSRF Token'}, status=403)

