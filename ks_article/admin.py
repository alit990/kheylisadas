from django.contrib import admin

from ks_article.models import Article, ArticleCategory, ArticleComment, ArticleVisit


# Register your models here.
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'title', 'category_id']

    class Meta:
        model = Article


class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'title', 'id']

    class Meta:
        model = ArticleCategory


class ArticleCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'create_date', 'parent','article']
    class Meta:
        model = ArticleComment


class ArticleVisitAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user']

    class Meta:
        model = ArticleVisit


admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleVisit, ArticleVisitAdmin)
admin.site.register(ArticleCategory, ArticleCategoryAdmin)
admin.site.register(ArticleComment, ArticleCommentAdmin)
