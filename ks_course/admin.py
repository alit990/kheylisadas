from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from ks_course.models import Course, SectionCourse, CourseComment, CourseVisit, TransactionCourse, GiftCourse


# Register your models here.
class CourseAdmin(GuardedModelAdmin):
    list_display = ['__str__', 'title', 'price', 'is_active']

    class Meta:
        model = Course


class SectionCourseAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'title', 'course', 'is_active']

    class Meta:
        model = SectionCourse


class CourseCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'create_date', 'parent']

    class Meta:
        model = CourseComment


class CourseVisitAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user']

    class Meta:
        model = CourseVisit


class TransactionCourseAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'payment', 'in_process', 'is_paid']

    class Meta:
        model = TransactionCourse


class GiftCourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'percentage', 'max', 'course', 'is_active', 'is_expired', 'start_date', 'end_date']

    class Meta:
        model = GiftCourse


admin.site.register(TransactionCourse, TransactionCourseAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(SectionCourse, SectionCourseAdmin)
admin.site.register(CourseComment, CourseCommentAdmin)
admin.site.register(CourseVisit, CourseVisitAdmin)
admin.site.register(GiftCourse, GiftCourseAdmin)
