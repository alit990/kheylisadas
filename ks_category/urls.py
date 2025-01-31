from django.urls import path
from .views import category_chapter_detail, category_detail, add_category_chapter_comment, WeeklyListView, \
    WeekDetailView, add_week_comment

urlpatterns = [
    path('<int:id>/<slug:slug>', category_detail, name='category-detail'),
    # path('<int:category_id>/<int:chapter_id>/<slug:chapter_slug>', category_chapter_detail, name='category-chapter-detail'),
    path('<int:category_id>/<int:chapter_id>/<slug:chapter_slug>/', category_chapter_detail, name='category-chapter-detail'),

    path('add-category-chapter-comment', add_category_chapter_comment, name='add_category_chapter_comment'),

    path('weekly', WeeklyListView.as_view(), name='weekly'),
    path('weekly/<pk>/', WeekDetailView.as_view(), name='week_detail'),
    path('add-week-comment', add_week_comment, name='add_week_comment'),


    # path('<int:category_id>', views.category_detail, name='category-detail'),
]
