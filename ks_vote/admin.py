from django.contrib import admin

from ks_vote.models import ArticleVote, AudioVote, CCDetailVote, WeekVote, CourseVote, Question, UserAnswer, \
    AudioPlaylist, AudioWeekPlaylist, AudioCourseVote, AudioWeekVote


# Register your models here.
class ArticleVoteAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'article', 'user', 'vote']

    class Meta:
        model = ArticleVote


class AudioVoteAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'audio', 'user', 'vote']

    class Meta:
        model = AudioVote


class AudioCourseVoteAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'audio', 'user', 'vote']

    class Meta:
        model = AudioCourseVote


class AudioWeekVoteAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'audio', 'user', 'vote']

    class Meta:
        model = AudioWeekVote


class CCDetailVoteAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'ccdetail', 'user', 'vote']

    class Meta:
        model = CCDetailVote


class WeekVoteAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'week', 'user', 'vote']

    class Meta:
        model = WeekVote


class CourseVoteAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'course', 'user', 'vote']

    class Meta:
        model = CourseVote


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'text', 'audio', 'answer']

    class Meta:
        model = Question


class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'create_date']

    class Meta:
        model = UserAnswer


class AudioPlaylistAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'audio', 'user', 'is_delete']

    class Meta:
        model = AudioPlaylist


class AudioWeekPlaylistAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'audio', 'user', 'is_delete']

    class Meta:
        model = AudioWeekPlaylist


admin.site.register(ArticleVote, ArticleVoteAdmin)
admin.site.register(AudioVote, AudioVoteAdmin)
admin.site.register(AudioCourseVote, AudioCourseVoteAdmin)
admin.site.register(AudioWeekVote, AudioWeekVoteAdmin)
admin.site.register(CCDetailVote, CCDetailVoteAdmin)
admin.site.register(WeekVote, WeekVoteAdmin)
admin.site.register(CourseVote, CourseVoteAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(UserAnswer, UserAnswerAdmin)
admin.site.register(AudioPlaylist, AudioPlaylistAdmin)
admin.site.register(AudioWeekPlaylist, AudioWeekPlaylistAdmin)
