from django.contrib import admin

from ks_tag.models import TagCourse, TagArticle, TagCCDetail, TagWeek


class TagCourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active']

    class Meta:
        model = TagCourse


class TagArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active']

    class Meta:
        model = TagArticle


class TagCCDetailAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active']

    class Meta:
        model = TagCCDetail


class TagWeekAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active']

    class Meta:
        model = TagWeek


admin.site.register(TagCourse, TagCourseAdmin)
admin.site.register(TagArticle, TagArticleAdmin)
admin.site.register(TagCCDetail, TagCCDetailAdmin)
admin.site.register(TagWeek, TagWeekAdmin)
