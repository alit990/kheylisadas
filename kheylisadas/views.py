from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect

from ks_account.models import User
from ks_article.models import Article
from ks_audio.models import Audio, AudioWeek
from ks_category.models import Category
from ks_course.models import Course
from ks_site.models import Reference, SiteSetting
from ks_subscription.models import Plan, Transaction
from utility.utils import group_subscription_name, codename_audio_perm, codename_audio_week_perm


# header code behind
def header(request, *args, **kwargs):
    site_setting = SiteSetting.objects.filter(is_main_setting=True).first()

    # print(site_setting)

    has_perm = False
    if request.user.is_authenticated:
        user_id = request.user.id
        current_user: User = User.objects.filter(id=user_id, is_active=True).first()

        # permission group for subscription
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

    context = {
        'site_setting': site_setting,
        'has_perm': has_perm
    }
    return render(request, 'shared/Header.html', context)


# footer code behind
def footer(request, *args, **kwargs):
    site_setting = SiteSetting.objects.filter(is_main_setting=True).first()
    categories = Category.objects.all()
    courses = Course.objects.filter(is_active=True)
    context = {
        'site_setting': site_setting,
        'categories': categories,
        'courses': courses,
    }
    return render(request, 'shared/Footer.html', context)


def index_page(request):
    context = {}
    return render(request, 'errors/404.html', context)


def home_page(request):
    categories = Category.objects.all()
    articles = Article.objects.get_active_articles()
    courses = Course.objects.filter(is_active=True)
    references = Reference.objects.filter(is_active=True)
    site_setting = SiteSetting.objects.filter(is_main_setting=True).first()
    plans = Plan.objects.filter(is_active=True)
    # print(categories)
    has_perm = False
    if request.user.is_authenticated:
        user_id = request.user.id
        current_user: User = User.objects.filter(id=user_id, is_active=True).first()

        # permission group for subscription
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

    context = {
        'categories': categories,
        'articles': articles,
        'courses': courses,
        'plans': plans,
        'has_perm': has_perm,
        'references': references,
        'site_setting': site_setting,
    }
    return render(request, 'home_page.html', context)


def success_page(request):
    # print(request)
    context = {
        'data': '',
    }
    return render(request, 'success_page.html', context)


def failure_page(request):
    if not request.COOKIES.get('message_shown'):
        response = render(request, 'failure_page.html', {'data': ''})
        response.set_cookie('message_shown', 'yes', max_age=10)  # کوکی برای 10 ثانیه
        return response
    else:
        return redirect('home_page')


# def failure_page(request):
#     context = {
#         'data': '',
#     }
#     return render(request, 'failure_page.html', context)


def custom_page_not_found_view_404(request, exception):
    return render(request, "errors/404.html", {})


def custom_error_view_500(request, exception=None):
    return render(request, "errors/500.html", {})


def custom_permission_denied_view_403(request, exception=None):
    return render(request, "errors/403.html", {})


def custom_bad_request_view_400(request, exception=None):
    return render(request, "errors/400.html", {})


def maintenance_view(request):
    return render(request, 'maintenance.html')
