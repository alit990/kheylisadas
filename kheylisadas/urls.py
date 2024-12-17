from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from kheylisadas import settings
from .views import home_page, header, footer, index_page, success_page, failure_page

urlpatterns = [
    path('index', index_page, name="home_page"),
    # path('index', index_page, name="home_page"),
    path('', home_page, name="home_page"),
    path('success', success_page, name="success_page"),
    path('failure', failure_page, name="failure_page"),
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
    # path('admin/', admin.site.urls),
    path('core/', include('core.urls')),  # for webpack
    path('captcha/', include('captcha.urls')),  # capthca urls
    path('ckeditor/', include('ckeditor_uploader.urls')),  # ckeditor uploader urls

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
