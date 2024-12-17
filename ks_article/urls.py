from django.urls import path

from ks_article.views import ArticlesList, ArticlesListByCategory, articles_categories_partial, \
    ArticleDetailView, add_article_comment, articles_all_tags_partial, ArticlesListByTag, recent_articles_partial

urlpatterns = [
    path('', ArticlesList.as_view() , name='articles_list'),
    path('<slug:category_slug>/', ArticlesListByCategory.as_view(), name='articles_list_by_category'),
    path('tag/<slug:slug>/', ArticlesListByTag.as_view(), name='articles_list_by_tag'),
    path('<int:pk>/<slug:slug>', ArticleDetailView.as_view(), name='article_detail'),

    path('article_categories_partial', articles_categories_partial, name='articles_categories_partial'),
    path('recent-articles-partial', recent_articles_partial, name='recent_articles_partial'),
    path('articles_all_tags_partial', articles_all_tags_partial, name='articles_all_tags_partial'),
    path('add-article-comment', add_article_comment, name='add_article_comment')
]


