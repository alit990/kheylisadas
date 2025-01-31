from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models import Q
from django.http import QueryDict
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ks_audio.models import Audio, AudioVisit, AudioCourse, AudioWeek, AudioCourseVisit, AudioWeekVisit, AudioChapter, \
    AudioCourseChapter, AudioWeekChapter, AudioArticleChapter, AudioArticle, FileAttachment, VideoAttachment

from .models import Audio, AudioChapter
from .forms import AudioChapterForm
from django import forms
from django_select2.forms import Select2Widget
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Audio

from django.contrib.admin.views.main import ChangeList



class AudioChapterInline(admin.TabularInline):
    model = AudioChapter
    form = AudioChapterForm  # استفاده از فرم سفارشی
    extra = 1  # تعداد فرم‌های خالی اضافی که نمایش داده می‌شود


# class AudioAdmin(admin.ModelAdmin):
#     list_display = ['__str__', 'title', 'section', 'order', 'type']
#     list_editable = ('order',)
#     inlines = [AudioChapterInline]  # اضافه کردن inline
#
#     class Meta:
#         model = Audio


class AudioAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'title', 'section', 'order', 'type']
    list_editable = ('order',)
    actions = ['duplicate_audio']  # اضافه کردن اکشن
    inlines = [AudioChapterInline]  # اضافه کردن inline
    search_fields = ['name', 'title', 'section__name', 'section__ccdetail__name']  # فیلدهای قابل جستجو را مشخص کنید


    # def get_search_fields(self, request):
    #     return []  # غیرفعال کردن فیلد جستجوی پیشفرض ادمین

    def get_ordering(self, request):  # Correct way to handle ordering
        return ['order']  # Or whatever your default ordering should be


    # def changelist_view(self, request, extra_context=None):
    #     extra_context = extra_context or {}
    #     form = AudioSearchForm(request.GET or None)
    #     extra_context['audio_search_form'] = form
    #
    #     queryset = self.get_queryset(request)
    #
    #     search_term = request.GET.get('search_term')
    #     if search_term:
    #         queryset = queryset.filter(id=search_term)
    #
    #     cl = CustomChangeList(
    #         request, self.model, self.list_display,
    #         self.list_display_links, self.list_filter,
    #         self.date_hierarchy, self.search_fields,
    #         self.list_select_related, self.list_per_page,
    #         self.list_max_show_all, self.list_editable,
    #         self, sortable_by=[], search_help_text=""
    #     )
    #
    #     # تنظیم `queryset` برای استفاده در قالب
    #     cl.queryset = queryset
    #
    #     context = {
    #         **self.admin_site.each_context(request),
    #         'title': cl.title,
    #         'cl': cl,
    #         'media': self.media,
    #         'has_add_permission': self.has_add_permission(request),
    #         'opts': getattr(self.model, '_meta'),
    #         'add_url': f'/ks-admin-panel/ks_audio/audio/add/',  # مسیر افزودن رکورد
    #         'audio_search_form': form,
    #     }
    #     context.update(extra_context)
    #
    #     return TemplateResponse(request, self.change_list_template or 'admin/ks_audio/audio/change_list.html', context)

    def duplicate_audio(self, request, queryset):
        for obj in queryset:
            original_id = obj.id  # ذخیره آی‌دی اصلی
            obj.id = None  # reset the ID to create a new instance
            obj.save()
            self.message_user(request, f"رکورد با آی‌دی {original_id} کپی شد. آی‌دی جدید: {obj.id}")

            # کپی کردن inline ها
            audio_chapters = AudioChapter.objects.filter(
                audio=original_id)  # فیلتر کردن inline ها با استفاده از آی‌دی اصلی
            for chapter in audio_chapters:
                chapter.id = None  # reset the ID to create a new instance
                chapter.audio = obj  # تنظیم audio به رکورد جدید
                chapter.save()

            # redirect to the edit page of the newly created record
            # return redirect(f'/admin/{obj._meta.app_label}/{obj._meta.model_name}/{obj.pk}/change/')
            new_admin_url = f'/ks-admin-panel/{obj._meta.app_label}/{obj._meta.model_name}/{obj.pk}/change/'
            return redirect(new_admin_url)

    duplicate_audio.short_description = "کپی کردن رکوردهای انتخاب شده به همراه فصل‌ها"

    class Meta:
        model = Audio


admin.site.register(Audio, AudioAdmin)


# class AudioAdmin(admin.ModelAdmin):
#     list_display = ['__str__', 'title', 'section', 'order', 'type']
#     list_editable = ('order',)
#
#     class Meta:
#         model = Audio


class AudioCourseAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'title', 'section_course']

    class Meta:
        model = AudioCourse


class AudioWeekAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'title', 'section_week']

    class Meta:
        model = AudioWeek


class AudioVisitAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user']

    class Meta:
        model = AudioVisit


class AudioCourseVisitAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user']

    class Meta:
        model = AudioCourseVisit


class AudioWeekVisitAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user']

    class Meta:
        model = AudioWeekVisit


class AudioChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'start_time', 'start_time_seconds', 'create_date', 'is_active', 'is_delete')
    readonly_fields = ('start_time_seconds',)


class AudioCourseChapterAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'title', 'audio', 'start_time']

    class Meta:
        model = AudioCourseChapter


class AudioWeekChapterAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'title', 'audio', 'start_time']

    class Meta:
        model = AudioWeekChapter


admin.site.register(AudioCourse, AudioCourseAdmin)
admin.site.register(AudioWeek, AudioWeekAdmin)
admin.site.register(AudioVisit, AudioVisitAdmin)
admin.site.register(AudioCourseVisit, AudioCourseVisitAdmin)
admin.site.register(AudioWeekVisit, AudioWeekVisitAdmin)
admin.site.register(AudioChapter, AudioChapterAdmin)
admin.site.register(AudioCourseChapter, AudioCourseChapterAdmin)
admin.site.register(AudioWeekChapter, AudioWeekChapterAdmin)
admin.site.register(AudioArticle)
admin.site.register(AudioArticleChapter)
admin.site.register(FileAttachment)
admin.site.register(VideoAttachment)
