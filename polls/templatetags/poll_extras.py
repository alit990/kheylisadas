from django import template
from jalali_date import date2jalali

register = template.Library()


@register.filter(name='show_jalali_date')
def show_jalali_date(value):
    return date2jalali(value)


@register.filter
def is_active_filter(queryset):
    return queryset.filter(is_active=True)


#  برای قسمت کتگوری که tag های 1 تا 5 داشت
@register.filter
def mod(value, arg):
    return value % arg


@register.filter
def truncate_to_one_line(value, length=50):
    if len(value) > length:
        return value[:length] + '...'
    return value


# برای success messages و جدا کردن مقادیر ثبت شده داخل extra_tags
@register.filter
def split_custom(value, arg):
    return value.split(arg)

@register.filter
def key_value_custom(value):
    return value.split('=')
