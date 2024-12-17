from django.contrib import admin

from ks_category.models import Chapter, Category, CCDetail, Section, CCDetailComment, Week, WeekComment, SectionWeek, \
    CCDetailVisit, WeekVisit


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'title', 'slug', 'is_active']

    class Meta:
        model = Category


class ChapterAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'title', 'slug', 'is_active']

    class Meta:
        model = Chapter


class CCDetailAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'title', 'category_id', 'chapter_id', 'is_active']

    class Meta:
        model = CCDetail


class SectionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'title', 'ccdetail_id']

    class Meta:
        model = Section


class CCDetailCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'create_date', 'parent', 'ccdetail']

    class Meta:
        model = CCDetailComment


class WeekAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'title', 'is_active']

    class Meta:
        model = Week


class WeekCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'create_date', 'parent', 'week']

    class Meta:
        model = WeekComment


class SectionWeekAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'title', 'week_id']

    class Meta:
        model = SectionWeek


class CCDetailVisitAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user']

    class Meta:
        model = CCDetailVisit


class WeekVisitAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user']

    class Meta:
        model = WeekVisit


admin.site.register(Category, CategoryAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(CCDetail, CCDetailAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(CCDetailComment, CCDetailCommentAdmin)
admin.site.register(Week, WeekAdmin)
admin.site.register(WeekComment, WeekCommentAdmin)
admin.site.register(SectionWeek, SectionWeekAdmin)
admin.site.register(CCDetailVisit, CCDetailVisitAdmin)
admin.site.register(WeekVisit, WeekVisitAdmin)
