import json
import time

from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from datetime import datetime, timedelta

from ks_account.models import User
from ks_audio.models import Audio, AudioChapter, AudioWeek, AudioWeekChapter
from ks_category.models import Category, CCDetail, Section, CCDetailComment, Week, WeekComment, SectionWeek, WeekVisit, \
    CCDetailVisit, Chapter
from ks_site.models import Avatar
from ks_subscription.models import Transaction
from ks_vote.forms import QuestionForm
from ks_vote.models import WeekVote, CCDetailVote, AudioVote, AudioPlaylist, AudioWeekVote, AudioWeekPlaylist
from utility.context_audio_with_section_preparation import D, Sec, Au, Ch
from utility.context_chapter_preparation import MyChapter, MyChapterData
from utility.http_service import get_client_ip
from utility.utils import group_subscription_name, codename_audio_perm, codename_audio_week_perm


# محل نمایش chapter های مختلف یک category
def category_detail(request, id=None, slug=None):
    category = Category.objects.filter(id=id, is_active=True).first()
    chapters = category.chapters.all()

    my_chapters = []
    ccdetails = CCDetail.objects.filter(category_id=category.id, is_active=True, is_delete=False)
    for ccdetail in ccdetails:
        chapter: Chapter = ccdetail.chapter
        my_chapter = MyChapter(id=chapter.id, title=chapter.title, name=chapter.name, slug=chapter.slug,
                               audio_url=ccdetail.audio_url)
        my_chapters.append(my_chapter)
    my_chapter_data = MyChapterData('chapter_data')
    my_chapter_data.add_chapter("chapters", my_chapters)
    data_js = str(my_chapter_data).replace("\'", "\"")
    data = json.loads(data_js)

    context = {
        'category': category,
        'chapters': chapters,
        'data': data
    }
    if 'pergnancy' in category.title:
        try:
            week = Week.objects.filter(audio_url__isnull=False).first()
            week_audio_url = week.audio_url
            context['WEEK_AUDIO_URL'] = week_audio_url
        except:
            context['WEEK_AUDIO_URL'] = ""

    return render(request, 'category_detail.html', context)


def category_chapter_detail(request, category_id=None, chapter_id=None, chapter_slug=None):
    has_perm = False
    # todo: MultipleObjectsReturned if be eshtebah 2 bar data sabt shode bashad
    ccdetail = CCDetail.objects.get_details_by_category_chapter(category_id=category_id,
                                                                chapter_id=chapter_id)  # using 404
    # sections = get_object_or_404(Section,ccdetail_id=ccdetail.id)
    sections = Section.objects.filter(ccdetail_id=ccdetail.id, is_active=True)
    comments = CCDetailComment.objects.filter(ccdetail_id=ccdetail.id, parent=None,
                                              is_allowed=True).order_by('-create_date').prefetch_related(
        'ccdetailcomment_set')
    comments_count = CCDetailComment.objects.filter(ccdetail_id=ccdetail.id, is_allowed=True).count()
    tags = ccdetail.tags.all()
    user_ip = get_client_ip(request)
    user_id = None
    if request.user.is_authenticated:
        user_id = request.user.id
        current_user: User = User.objects.filter(id=user_id, is_active=True).first()
        # permission group for subscription
        has_perm = current_user.groups.filter(name=group_subscription_name()).exists()
        print("has perm?", has_perm)
        if Transaction.objects.filter(user_id=current_user.id, is_paid=True, is_expired=False).exists() and has_perm:
            transaction: Transaction = Transaction.objects.filter(
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
                has_perm = False

    has_been_visited = CCDetailVisit.objects.filter(ip__iexact=user_ip, ccdetail_id=ccdetail.id).exists()
    if not has_been_visited:
        new_visit = CCDetailVisit(ip=user_ip, user_id=user_id, ccdetail_id=ccdetail.id)
        new_visit.save()

    context = {'ccdetail': ccdetail, 'sections': sections, 'comments': comments, 'comments_count': comments_count,
               'tags': tags,
               'ccdetail_likes_count': CCDetailVote.objects.filter(ccdetail_id=ccdetail.id, vote=1).count(),
               'ccdetail_dislikes_count': CCDetailVote.objects.filter(ccdetail_id=ccdetail.id, vote=0).count(),
               'ccdetail_user_vote': -1}

    if CCDetailVote.objects.filter(ccdetail_id=ccdetail.id, user_id=user_id).exists():
        context['ccdetail_user_vote'] = CCDetailVote.objects.filter(ccdetail_id=ccdetail.id,
                                                                    user_id=user_id).first().vote
    avatar = Avatar.objects.filter(is_main=True).first()
    context['avatar'] = avatar
    audio_count = 0
    d = D(ccdetail.title)
    sec = []
    for section in sections:
        s = Sec(id=section.id, title=section.title, name=section.name, description=section.description)
        audio_set = Audio.objects.filter(section_id=section.id, is_active=True)
        audio_count += audio_set.count()
        au = []
        for audio in audio_set:
            added_playlist = False
            like_count = AudioVote.objects.filter(audio_id=audio.id, vote=1).count()
            dislike_count = AudioVote.objects.filter(audio_id=audio.id, vote=0).count()
            user_vote = -1
            if request.user.is_authenticated:
                if AudioVote.objects.filter(audio_id=audio.id, user_id=user_id).exists():
                    user_vote = AudioVote.objects.filter(audio_id=audio.id, user_id=user_id).first().vote
                if AudioPlaylist.objects.filter(user_id=user_id, audio_id=audio.id, is_delete=False).exists():
                    added_playlist = True
            else:
                if AudioVote.objects.filter(audio_id=audio.id, ip=user_ip).exists():
                    user_vote = AudioVote.objects.filter(audio_id=audio.id, ip=user_ip).first().vote

            if audio.is_lock and not has_perm:
                a = Au(id=audio.id, title=audio.title, name=audio.name,
                       description=audio.description, is_lock=audio.is_lock)
            else:
                a = Au(id=audio.id, title=audio.title, name=audio.name,
                       description=audio.description, is_lock=audio.is_lock, type=audio.type,
                       like_count=like_count, dislike_count=dislike_count,
                       fake_like_count=audio.fake_like_count, fake_dislike_count=audio.fake_dislike_count,
                       user_vote=user_vote, added_playlist=added_playlist)
            chapter_set = AudioChapter.objects.filter(audio_id=audio.id, is_active=True)
            ch = []
            for chapter in chapter_set:
                c = Ch(title=chapter.title, name=chapter.name, start_time=chapter.start_sec())
                ch.append(c)
            a.add_chapter("chapters", ch)
            au.append(a)
        s.add_audio("audios", au)
        sec.append(s)
    d.add_section("sections", sec)
    data_js = str(d).replace("\'", "\"")
    data = json.loads(data_js)
    context['data'] = data
    context['data_js'] = data_js
    context['has_perm'] = has_perm
    # question_form = QuestionForm()
    # context['question_form'] = question_form
    context['audio_count'] = audio_count

    return render(request, 'category_chapter_detail.html', context)


def add_category_chapter_comment(request: HttpRequest):
    if request.user.is_authenticated:
        current_user = request.user
        ccdetail_id = request.GET.get('ccdetail_id')
        ccdetail_comment = request.GET.get('ccdetail_comment')
        parent_id = request.GET.get('parent_id')
        if request.user.is_staff:
            new_comment = CCDetailComment(ccdetail_id=ccdetail_id, text=ccdetail_comment, user_id=request.user.id,
                                          parent_id=parent_id, is_allowed=True)
            new_comment.save()
            context = {
                'comments': CCDetailComment.objects.filter(ccdetail_id=ccdetail_id, parent=None,
                                                           is_allowed=True).order_by(
                    '-create_date').prefetch_related('ccdetailcomment_set'),
                'comments_count': CCDetailComment.objects.filter(ccdetail_id=ccdetail_id, is_allowed=True).count()
            }
            return render(request, 'includes/comments_partial.html', context)
        else:
            limit_minutes_ago = datetime.now() - timedelta(minutes=15)
            comment_count_in_last_limit_min = CCDetailComment.objects.filter(
                Q(create_date__gte=limit_minutes_ago) & Q(user=current_user)).count()
            if comment_count_in_last_limit_min < 3:
                new_comment = CCDetailComment(ccdetail_id=ccdetail_id, text=ccdetail_comment, user_id=request.user.id,
                                              parent_id=parent_id)
                new_comment.save()
                return HttpResponse('no-staff')
            else:
                return HttpResponse('too-many-comment')
    return HttpResponse('response')


class WeeklyListView(ListView):
    model = Week
    paginate_by = 40
    template_name = 'weekly_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(WeeklyListView, self).get_context_data(*args, **kwargs)
        return context

    def get_queryset(self):
        query = super(WeeklyListView, self).get_queryset()
        query = query.filter(is_active=True)
        return query


class WeekDetailView(DetailView):
    model = Week
    template_name = 'week_detail.html'

    def get_queryset(self):
        query = super(WeekDetailView, self).get_queryset()
        query = query.filter(is_active=True)
        return query

    def get_context_data(self, **kwargs):
        context = super(WeekDetailView, self).get_context_data()
        week: Week = kwargs.get('object')
        has_perm = False
        avatar = Avatar.objects.filter(is_main=True).first()
        context['avatar'] = avatar
        week: Week = kwargs.get('object')
        sections = SectionWeek.objects.filter(week_id=week.id, is_active=True)
        comments = WeekComment.objects.filter(week_id=week.id, parent=None,
                                              is_allowed=True).order_by('-create_date').prefetch_related(
            'weekcomment_set')
        comments_count = WeekComment.objects.filter(week_id=week.id, is_allowed=True).count()
        tags = week.tags.all()
        user_ip = get_client_ip(self.request)
        user_id = None
        if self.request.user.is_authenticated:
            user_id = self.request.user.id
            current_user: User = User.objects.filter(id=user_id, is_active=True).first()
            # permission group for subscription
            has_perm = current_user.groups.filter(name=group_subscription_name()).exists()
            print("has perm?", has_perm)
            if Transaction.objects.filter(user_id=current_user.id, is_paid=True,
                                          is_expired=False).exists() and has_perm:
                transaction: Transaction = Transaction.objects.filter(
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
                    has_perm = False

        has_been_visited = WeekVisit.objects.filter(ip__iexact=user_ip, week_id=week.id).exists()
        if not has_been_visited:
            new_visit = WeekVisit(ip=user_ip, user_id=user_id, week_id=week.id)
            new_visit.save()

        context['week'] = week
        context['sections'] = sections
        context['comments'] = comments
        context['comments_count'] = comments_count
        context['tags'] = tags
        context['week_likes_count'] = WeekVote.objects.filter(week_id=week.id, vote=1).count()
        context['week_dislikes_count'] = WeekVote.objects.filter(week_id=week.id, vote=0).count()
        context['week_user_vote'] = -1
        if WeekVote.objects.filter(week_id=week.id, user_id=user_id).exists():
            context['week_user_vote'] = WeekVote.objects.filter(week_id=week.id, user_id=user_id).first().vote

        audio_count = 0
        d = D(week.title)
        sec = []
        for section in sections:
            s = Sec(id=section.id, title=section.title, name=section.name, description=section.description)
            audio_set = AudioWeek.objects.filter(section_week_id=section.id, is_active=True)
            audio_count += audio_set.count()
            au = []
            for audio in audio_set:
                added_playlist = False
                like_count = AudioWeekVote.objects.filter(audio_id=audio.id, vote=1).count()
                dislike_count = AudioWeekVote.objects.filter(audio_id=audio.id, vote=0).count()
                user_vote = -1
                if self.request.user.is_authenticated:
                    if AudioWeekVote.objects.filter(audio_id=audio.id, user_id=user_id).exists():
                        user_vote = AudioWeekVote.objects.filter(audio_id=audio.id, user_id=user_id).first().vote
                    if AudioWeekPlaylist.objects.filter(user_id=user_id, audio_id=audio.id, is_delete=False).exists():
                        added_playlist = True
                else:
                    if AudioWeekVote.objects.filter(audio_id=audio.id, ip=user_ip).exists():
                        user_vote = AudioWeekVote.objects.filter(audio_id=audio.id, ip=user_ip).first().vote

                if audio.is_lock and not has_perm:
                    a = Au(id=audio.id, title=audio.title, name=audio.name,
                           description=audio.description, is_lock=audio.is_lock)
                else:
                    a = Au(id=audio.id, title=audio.title, name=audio.name,
                           description=audio.description, is_lock=audio.is_lock, type=audio.type,
                           like_count=like_count, dislike_count=dislike_count,
                           fake_like_count=audio.fake_like_count, fake_dislike_count=audio.fake_dislike_count,
                           user_vote=user_vote, added_playlist=added_playlist)
                chapter_set = AudioWeekChapter.objects.filter(audio_id=audio.id, is_active=True)
                ch = []
                for chapter in chapter_set:
                    c = Ch(title=chapter.title, name=chapter.name, start_time=chapter.start_sec())
                    ch.append(c)
                a.add_chapter("chapters", ch)
                au.append(a)
            s.add_audio("audios", au)
            sec.append(s)
        d.add_section("sections", sec)
        data_js = str(d).replace("\'", "\"")
        data = json.loads(data_js)
        context['data'] = data
        context['data_js'] = data_js
        context['has_perm'] = has_perm
        # question_form = QuestionForm()
        # context['question_form'] = question_form
        context['audio_count'] = audio_count
        # context['duration'] = time.strftime("%H:%M:%S", time.gmtime(duration_sec))
        return context


def add_week_comment(request: HttpRequest):
    if request.user.is_authenticated:
        current_user = request.user
        week_id = request.GET.get('week_id')
        week_comment = request.GET.get('week_comment')
        parent_id = request.GET.get('parent_id')
        if request.user.is_staff:
            new_comment: WeekComment = WeekComment(week_id=week_id, text=week_comment, user_id=request.user.id,
                                                   parent_id=parent_id, is_allowed=True)
            new_comment.save()
            context = {
                'comments': WeekComment.objects.filter(week_id=week_id, parent=None, is_allowed=True).order_by(
                    '-create_date').prefetch_related('weekcomment_set'),
                'comments_count': WeekComment.objects.filter(week_id=week_id, is_allowed=True).count()
            }
            return render(request, 'includes/comments_partial.html', context)
        else:
            limit_minutes_ago = datetime.now() - timedelta(minutes=15)
            comment_count_in_last_limit_min = WeekComment.objects.filter(
                Q(create_date__gte=limit_minutes_ago) & Q(user=current_user)).count()
            if comment_count_in_last_limit_min < 3:
                new_comment = WeekComment(week_id=week_id, text=week_comment, user_id=request.user.id,
                                          parent_id=parent_id)
                new_comment.save()
                return HttpResponse('no-staff')
            else:
                return HttpResponse('too-many-comment')
    return HttpResponse('response')





