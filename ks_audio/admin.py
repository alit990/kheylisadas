from django.contrib import admin

from ks_audio.models import Audio, AudioVisit, AudioCourse, AudioWeek, AudioCourseVisit, AudioWeekVisit, AudioChapter, \
    AudioCourseChapter, AudioWeekChapter, AudioArticleChapter, AudioArticle


class AudioAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'title', 'section', 'type']

    class Meta:
        model = Audio


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
    list_display = ['__str__', 'title', 'audio', 'start_time']

    class Meta:
        model = AudioChapter


class AudioCourseChapterAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'title', 'audio', 'start_time']

    class Meta:
        model = AudioCourseChapter


class AudioWeekChapterAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'title', 'audio', 'start_time']

    class Meta:
        model = AudioWeekChapter


admin.site.register(Audio, AudioAdmin)
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
