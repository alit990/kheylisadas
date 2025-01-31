import json

from django.db.models import Q
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from datetime import datetime, timedelta

from ks_account.models import User
from ks_article.models import Article, ArticleCategory, ArticleComment, ArticleVisit
from ks_audio.models import AudioArticleChapter
from ks_site.models import Avatar, SiteSetting
from ks_tag.models import Tag
from ks_vote.models import ArticleVote, AudioArticleVote
from utility.context_audio_no_section_preparation import D, Au, Ch
from utility.http_service import get_client_ip


class ArticlesList(ListView):
    template_name = 'articles_list.html'
    paginate_by = 6

    def get_queryset(self):
        return Article.objects.get_active_articles().order_by('id')


class ArticlesListByCategory(ListView):
    template_name = 'articles_list.html'
    paginate_by = 2

    def get_context_data(self, **kwargs):
        context = super(ArticlesListByCategory, self).get_context_data()
        site_setting = SiteSetting.objects.filter(is_main_setting=True).first()
        if site_setting.courses_is_disabled:
            raise Http404("Articles is disabled")
        return context

    def get_queryset(self):
        print(self.kwargs)
        category_slug = self.kwargs['category_slug']
        category: ArticleCategory = ArticleCategory.objects.filter(slug=category_slug).first()
        if category is None:
            raise Http404('صفحه ی مورد نظر یافت نشد')
        return Article.objects.get_articles_by_category_id(category.id)


class ArticlesListByTag(ListView):
    template_name = 'articles_list.html'
    paginate_by = 2

    def get_context_data(self, **kwargs):
        context = super(ArticlesListByTag, self).get_context_data()
        site_setting = SiteSetting.objects.filter(is_main_setting=True).first()
        if site_setting.courses_is_disabled:
            raise Http404("Articles is disabled")
        return context

    def get_queryset(self):
        tag_slug = self.kwargs['slug']
        tag = Tag.objects.filter(slug__iexact=tag_slug).first()
        if tag:
            articles = tag.article_set.all()
        else:
            articles = Article.objects.none()

        # todo: slug farsi tolid nemikone va agar dar url farsi bashe error marbut be codec mide
        if articles is None:
            raise Http404('صفحه ی مورد نظر یافت نشد')
        return articles


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'article_detail.html'

    def get_queryset(self):
        query = super(ArticleDetailView, self).get_queryset()
        query = query.filter(is_active=True)
        return query

    def get_context_data(self, **kwargs):
        site_setting = SiteSetting.objects.filter(is_main_setting=True).first()
        if site_setting.courses_is_disabled:
            raise Http404("Articles is disabled")
        context = super(ArticleDetailView, self).get_context_data()
        article: Article = kwargs.get('object')
        avatar = Avatar.objects.filter(is_main=True).first()
        context['avatar'] = avatar
        context['comments'] = ArticleComment.objects.filter(
            article_id=article.id, parent=None,
            is_allowed=True).order_by('-create_date').prefetch_related('articlecomment_set')
        context['comments_count'] = ArticleComment.objects.filter(article_id=article.id, is_allowed=True).count()
        context['tags'] = article.tags.all()

        user_ip = get_client_ip(self.request)
        user_id = None
        if self.request.user.is_authenticated:
            user_id = self.request.user.id

        has_been_visited = ArticleVisit.objects.filter(ip__iexact=user_ip, article_id=article.id).exists()

        if not has_been_visited:
            new_visit = ArticleVisit(ip=user_ip, user_id=user_id, article_id=article.id)
            new_visit.save()
        context['article_likes_count'] = ArticleVote.objects.filter(article_id=article.id, vote=1).count()
        context['article_dislikes_count'] = ArticleVote.objects.filter(article_id=article.id, vote=0).count()
        if ArticleVote.objects.filter(article_id=article.id, user_id=user_id).exists():
            # user_article_vote = ArticleVote.objects.filter(article_id=article.id, user_id=user_id).first()
            context['article_user_vote'] = ArticleVote.objects.filter(article_id=article.id,
                                                                      user_id=user_id).first().vote
        context['article_user_vote'] = -1
        related_courses = article.courses.filter(is_active=True)
        context['related_courses'] = related_courses
        # -------- Audios Preparation ------------
        audio_set = article.audios.all()
        audio_count = 0
        d = D(article.title)
        au = []
        for audio in audio_set:
            like_count = AudioArticleVote.objects.filter(audio_id=audio.id, vote=1).count()
            dislike_count = AudioArticleVote.objects.filter(audio_id=audio.id, vote=0).count()
            user_vote = -1
            if self.request.user.is_authenticated:
                if AudioArticleVote.objects.filter(audio_id=audio.id, user_id=user_id).exists():
                    user_vote = AudioArticleVote.objects.filter(audio_id=audio.id, user_id=user_id).first().vote
            else:
                if AudioArticleVote.objects.filter(audio_id=audio.id, ip=user_ip).exists():
                    user_vote = AudioArticleVote.objects.filter(audio_id=audio.id, ip=user_ip).first().vote

            # if audio.is_lock and not has_perm:
            #     a = Au(id=audio.id, title=audio.title, name=audio.name, image_url=audio.image.url,
            #            audio_url="LOCKED",
            #            description=audio.description, is_lock=audio.is_lock)
            # else:
            a = Au(id=audio.id, title=audio.title, name=audio.name,
                   description=audio.description, is_lock=audio.is_lock, type=audio.type,
                   like_count=like_count, dislike_count=dislike_count, model="Article",
                   fake_like_count=audio.fake_like_count, fake_dislike_count=audio.fake_dislike_count,
                   user_vote=user_vote, added_playlist=False)
            chapter_set = AudioArticleChapter.objects.filter(audio_id=audio.id, is_active=True)
            ch = []
            for chapter in chapter_set:
                c = Ch(title=chapter.title, name=chapter.name, start_time=chapter.start_sec())
                ch.append(c)
            a.add_chapter("chapters", ch)
            au.append(a)
        d.add_audio("audios", au)
        data_js = str(d).replace("\'", "\"")
        data = json.loads(data_js)
        context['data'] = data
        context['data_js'] = data_js
        return context


def articles_categories_partial(request):
    categories = ArticleCategory.objects.get_active_categories()
    context = {
        'categories': categories
    }
    return render(request, 'includes/article_categories_partial.html', context)


def recent_articles_partial(request):
    articles = Article.objects.get_active_articles().order_by('create_date')[:5]
    context = {
        'articles': articles
    }
    return render(request, 'includes/recent_articles_partial.html', context)


def add_article_comment(request: HttpRequest):
    if request.user.is_authenticated:
        current_user: User = User.objects.filter(id=request.user.id).first()
        article_id = request.GET.get('article_id')
        article_comment = request.GET.get('article_comment')
        parent_id = request.GET.get('parent_id')
        if request.user.is_staff:
            new_comment = ArticleComment(article_id=article_id, text=article_comment, user_id=request.user.id,
                                         parent_id=parent_id, is_allowed=True)
            new_comment.save()
            context = {
                'comments': ArticleComment.objects.filter(article_id=article_id, parent=None, is_allowed=True).order_by(
                    '-create_date').prefetch_related('articlecomment_set'),
                'comments_count': ArticleComment.objects.filter(article_id=article_id, is_allowed=True).count()
            }
            # return HttpResponse('response')
            return render(request, 'includes/comments_partial.html', context)
        else:
            limit_minutes_ago = datetime.now() - timedelta(minutes=15)
            comment_count_in_last_limit_min = ArticleComment.objects.filter(
                Q(create_date__gte=limit_minutes_ago) & Q(user=current_user)).count()
            print(f"comment count is {comment_count_in_last_limit_min}")
            if comment_count_in_last_limit_min < 3:
                new_comment = ArticleComment(article_id=article_id, text=article_comment, user_id=request.user.id,
                                             parent_id=parent_id)
                new_comment.save()
                return HttpResponse('no-staff')
            else:
                return HttpResponse('too-many-comment')

    return HttpResponse('response')


def articles_all_tags_partial(request):
    # tags = Tag.objects.filter(is_active=True).all()
    tags = Tag.objects.filter(article__isnull=False, is_active=True).distinct()
    context = {
        'tags': tags
    }
    return render(request, 'includes/articles_all_tags_partial.html', context)
