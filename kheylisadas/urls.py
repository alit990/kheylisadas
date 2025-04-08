from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from kheylisadas import settings
from .views import home_page, header, footer, index_page, success_page, failure_page, maintenance_view, service_worker, \
    manifest_version, check_login_status

urlpatterns = [
    path('maintenance/', maintenance_view, name='maintenance'),
    # path('index', index_page, name="home_page"),
    path('', home_page, name="home_page"),
    path('index', home_page, name="home_page"),
    path('success', success_page, name="success_page"),
    path('failure', failure_page, name="failure_page"),
    path('service-worker/', service_worker, name='service-worker'),
    path('manifest-version/', manifest_version, name='manifest_version'),
    path('check-login-status/', check_login_status, name='check_login_status'),

    path('', include('ks_account.urls')),
    path('', include('ks_category.urls')),
    path('audio/', include('ks_audio.urls')),
    path('courses/', include('ks_course.urls')),
    path('articles/', include('ks_article.urls')),
    path('subscription/', include('ks_subscription.urls')),
    path('votes/', include('ks_vote.urls')),
    path('user/', include('ks_user_panel.urls')),
    path('', include('ks_site.urls')),
    path('header', header, name="header"),
    path('footer', footer, name="footer"),
    path('ks-admin-panel/', admin.site.urls),
    path('ks-account/', include(('ks_account.urls', 'ks_account'), namespace='ks_account')), # اضافه کردن namespace
    # path('admin/', admin.site.urls),
    path('core/', include('core.urls')),  # for webpack
    path('captcha/', include('captcha.urls')),  # capthca urls
    # path('ckeditor/', include('ckeditor_uploader.urls')),  # ckeditor uploader urls
    path('ckeditor/', include('django_ckeditor_5.urls')),
    path('select2/', include('django_select2.urls')),
]
if settings.DEBUG:
    # add root static files
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # add media static files
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'kheylisadas.views.custom_page_not_found_view_404'
handler500 = 'kheylisadas.views.custom_error_view_500'
handler403 = 'kheylisadas.views.custom_permission_denied_view_403'
handler400 = 'kheylisadas.views.custom_bad_request_view_400'
