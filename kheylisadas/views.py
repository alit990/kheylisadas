from django.conf import settings
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect
import os

from guardian.shortcuts import remove_perm

from ks_account.models import User
from ks_article.models import Article
from ks_audio.models import Audio, AudioWeek
from ks_category.models import Category
from ks_course.models import Course
from ks_site.models import Reference, SiteSetting
from ks_subscription.models import Plan, Transaction, Campaign, CTransaction
from utility.utils import group_subscription_name, codename_audio_perm, codename_audio_week_perm
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET


# header code behind
def header(request, *args, **kwargs):
    site_setting = SiteSetting.objects.filter(is_main_setting=True).first()
    # permission group for campaign
    current_campaign = Campaign.objects.filter(is_active=True,
                                               is_published=True).first()  # todo: agar baadan campain jadid amad bayad barrasi shavad

    has_campaign = False
    has_perm = False
    if request.user.is_authenticated:
        current_user: User = request.user
        user_id = current_user.id

        # check campaign access using django-guardian

        has_campaign = current_user.has_perm('fully_view_campaign', current_campaign)  # guardian library
        if has_campaign:
            has_c_transaction = CTransaction.objects.filter(user_id=current_user.id, is_paid=True,
                                                            is_expired=False, campaign=current_campaign).exists()
            if has_c_transaction:
                c_transaction = CTransaction.objects.filter(user_id=current_user.id, is_paid=True,
                                                            is_expired=False, campaign=current_campaign).first()
                if c_transaction.is_expired_this:
                    remove_perm('fully_view_campaign', current_user, current_campaign)
                    has_campaign = False

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
        'has_perm': has_perm,
        'has_campaign': has_campaign,
        'active_campaign': current_campaign
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


# @require_GET
# def service_worker(request):
#     # تنظیم مسیر مطلق به فایل service-worker.js
#     service_worker_path = os.path.join(settings.BASE_DIR, 'assets', 'assets', 'js', 'service-worker.js')
#     try:
#         with open(service_worker_path, 'r', encoding='utf-8') as f:
#             response = HttpResponse(f.read(), content_type='application/javascript')
#             response['Service-Worker-Allowed'] = '/'
#             return response
#     except FileNotFoundError:
#         return HttpResponse("File not found", status=404)
#     except UnicodeDecodeError as e:
#         return HttpResponse(f"Unicode decode error: {e}", status=500)


# @require_GET
# def service_worker(request):
#     # تنظیم مسیر مطلق به فایل service-worker.js
#     service_worker_path = os.path.join(settings.BASE_DIR, 'assets', 'assets', 'js', 'service-worker.js')
#     try:
#         with open(service_worker_path, 'r', encoding='utf-8') as f:
#             response = HttpResponse(f.read(), content_type='application/javascript')
#             response['Service-Worker-Allowed'] = '/'
#             return response
#     except FileNotFoundError:
#         return HttpResponse("File not found", status=404)
#     except UnicodeDecodeError as e:
#         return HttpResponse(f"Unicode decode error: {e}", status=500)
# views.py
# views.py

@require_GET
def service_worker(request):
    service_worker_path = os.path.join(settings.BASE_DIR, 'assets', 'assets', 'js', 'service-worker.js')
    try:
        with open(service_worker_path, 'r', encoding='utf-8') as f:
            response = HttpResponse(f.read(), content_type='application/javascript')
            response['Service-Worker-Allowed'] = '/'
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            # ارسال اطلاعات محیط از طریق هدر
            response['X-Debug-Mode'] = 'true' if settings.DEBUG else 'false'
            response['X-Static-Prefix'] = '/statics/' if settings.DEBUG else '/static/'
        return response
    except FileNotFoundError:
        return HttpResponse("File not found", status=404)
    except UnicodeDecodeError as e:
        return HttpResponse(f"Unicode decode error: {e}", status=500)
def manifest_version(request):
    manifest_version = "1.0.36"  # مقدار MANIFEST_VERSION را اینجا قرار دهید
    return JsonResponse({'version': manifest_version})


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


@login_required
def check_login_status(request):
    return JsonResponse({'is_logged_in': True})
