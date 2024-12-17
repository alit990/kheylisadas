from datetime import timedelta

from django import template

register = template.Library()


@register.filter()
def smooth_timedelta(timedeltaobj:timedelta):
    """Convert a datetime.timedelta object into Days, Hours, Minutes, Seconds."""
    secs = timedeltaobj.seconds
    timetot = ""
    if secs > 86400:  # 60sec * 60min * 24hrs
        days = secs // 86400
        timetot += "{} روز".format(int(days))
        secs = secs - days * 86400

    if secs > 3600:
        hrs = secs // 3600
        timetot += " {} ساعت".format(int(hrs))
        secs = secs - hrs * 3600

    if secs > 60:
        mins = secs // 60
        timetot += " {} دقیقه".format(int(mins))
        secs = secs - mins * 60

    # if secs > 0:
    #     timetot += " {} ثانیه".format(int(secs))
    return timetot
