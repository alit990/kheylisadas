from django.shortcuts import render, redirect

from ks_article.models import Article
from ks_audio.models import Audio
from ks_category.models import Category
from ks_course.models import Course
from ks_site.models import Reference, SiteSetting


# header code behind
def header(request, *args, **kwargs):
    site_setting = SiteSetting.objects.filter(is_main_setting=True).first()
    # print(site_setting)
    context = {
        'site_setting': site_setting
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
    # print(categories)
    context = {
        'categories': categories,
        'articles': articles,
        'courses': courses,
        'references': references,
        'site_setting': site_setting
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
