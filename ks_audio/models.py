import random
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field

from ks_account.models import User
from ks_course.models import SectionCourse
from ks_tag.models import Tag
from utility.choices import KSChoices
from utility.utils import upload_audio_image_path, upload_audio_file_path, upload_audio_course_file_path, \
    get_random_number
from django.db import models
from googletrans import Translator
from datetime import timedelta
import time


class Audio(models.Model):  # for category chapter ( ccdetail )
    order = models.IntegerField(default=0)  # فیلد ترتیب
    title = models.CharField(max_length=150, null=True, blank=True)
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to=upload_audio_image_path, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    is_lock = models.BooleanField(default=True)
    summary = CKEditor5Field('Summary', config_name='default', null=True, blank=True)
    description = CKEditor5Field('Description', config_name='default', null=True, blank=True)
    references = CKEditor5Field('References', config_name='default', null=True, blank=True)
    section = models.ForeignKey('ks_category.Section', on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now, editable=False)
    type = models.IntegerField(choices=KSChoices.CHOICES_AUDIO_TYPE, null=False, blank=False)
    parent = models.ForeignKey('Audio', on_delete=models.DO_NOTHING, null=True, blank=True)
    # url = models.URLField(null=True, blank=True)
    demo_url = models.CharField(max_length=2083, null=True, blank=True)  # طول 2083 برای URL به طور عملی کافی است
    url = models.CharField(max_length=2083, null=True, blank=True)  # طول 2083 برای URL به طور عملی کافی است
    duration = models.DurationField(null=True, blank=True, default=timedelta(0))
    fake_played_count = models.IntegerField(default=get_random_number(10, 30))
    fake_like_count = models.IntegerField(default=get_random_number(10, 19))
    fake_dislike_count = models.IntegerField(default=get_random_number(1, 4))
    fake_visit_count = models.IntegerField(default=get_random_number(10, 25))
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f"{self.name} / {self.section} / {self.type}"

    class Meta:
        permissions = [("can_view_monetary_audio", "Can view monetary audio")]
        ordering = ['order']

    def save(self, *args, **kwargs):
        if self.name:
            if not self.title:
                start_time = time.time()
                try:
                    translator = Translator()
                    translation = translator.translate(self.name, src='fa', dest='en')
                    self.title = translation.text
                except Exception:
                    if time.time() - start_time >= 3:
                        self.title = f"audio-{self.id if self.id else 'new'}"  # در صورت خطا یا قطع اینترنت
        super(Audio, self).save(*args, **kwargs)


class AudioCourse(models.Model):  # for course ( maybe must has subscription )
    title = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    # icon = models.CharField(default='A', max_length=10)
    # thumb = models.ImageField(upload_to=upload_audio_image_path, null=True, blank=True)
    # image = models.ImageField(upload_to=upload_audio_image_path, null=True, blank=True)
    # file = models.FileField(upload_to=upload_audio_course_file_path, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    is_lock = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    section_course = models.ForeignKey(SectionCourse, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now, editable=False)
    url = models.URLField(max_length=200, null=True)
    duration = models.DurationField(null=True, blank=True)
    fake_played_count = models.IntegerField(default=5)
    fake_like_count = models.IntegerField(default=5)
    fake_dislike_count = models.IntegerField(default=5)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f"{self.name} / {self.section_course}"


class AudioWeek(models.Model):  # for week
    title = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to=upload_audio_image_path, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    is_lock = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    section_week = models.ForeignKey('ks_category.SectionWeek', on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now, editable=False)
    type = models.IntegerField(choices=KSChoices.CHOICES_AUDIO_TYPE, null=False, blank=False)
    parent = models.ForeignKey('AudioWeek', on_delete=models.DO_NOTHING, null=True, blank=True)
    url = models.URLField(max_length=200, null=True)
    duration = models.DurationField(null=True, blank=True)
    fake_played_count = models.IntegerField(default=5)
    fake_like_count = models.IntegerField(default=5)
    fake_dislike_count = models.IntegerField(default=5)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f"{self.name} / {self.section_week}"

    class Meta:
        permissions = [("can_view_monetary_audio_week", "Can view monetary audio week")]


class AudioArticle(models.Model):  # for articles
    title = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    # image = models.ImageField(upload_to=upload_audio_image_path, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    is_lock = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    create_date = models.DateTimeField(default=timezone.now, editable=False)
    type = models.IntegerField(choices=KSChoices.CHOICES_AUDIO_TYPE, null=False, blank=False)
    url = models.URLField(max_length=200, null=True)
    duration = models.DurationField(null=True, blank=True)
    fake_played_count = models.IntegerField(default=5)
    fake_like_count = models.IntegerField(default=8)
    fake_dislike_count = models.IntegerField(default=1)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f"{self.name}"


class AudioVisit(models.Model):
    audio = models.ForeignKey('Audio', on_delete=models.CASCADE)
    ip = models.CharField(max_length=30)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f'{self.audio.title} / {self.ip}'


class AudioCourseVisit(models.Model):  # todo: just model created . not completed
    audio_course = models.ForeignKey('AudioCourse', on_delete=models.CASCADE)
    ip = models.CharField(max_length=30)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f'{self.audio_course.title} / {self.ip}'


class AudioWeekVisit(models.Model):  # todo: just model created . not completed
    audio_week = models.ForeignKey('AudioWeek', on_delete=models.CASCADE)
    ip = models.CharField(max_length=30)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f'{self.audio_week.title} / {self.ip}'


import random
from django.db import models
from django.utils import timezone

class AudioChapter(models.Model):
    title = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    audio = models.ForeignKey(Audio, on_delete=models.CASCADE)
    start_time = models.CharField(max_length=10)
    start_time_seconds = models.IntegerField(editable=False, default=0)  # فیلد جدید برای زمان شروع به ثانیه
    create_date = models.DateTimeField(default=timezone.now, editable=False)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def start_sec(self):
        """Get seconds from start_time."""
        m, s = self.start_time.split(':')
        return int(m) * 60 + int(s)

    def save(self, *args, **kwargs):
        self.start_time_seconds = self.start_sec()
        if self.name:
            if not self.title:
                start_time = time.time()
                try:
                    translator = Translator()
                    translation = translator.translate(self.name, src='fa', dest='en')
                    self.title = translation.text
                except Exception:
                    if time.time() - start_time >= 3:
                        self.title = f"audio-chapter-{self.id if self.id else 'new'}"
        super(AudioChapter, self).save(*args, **kwargs)

    class Meta:
        ordering = ['start_time_seconds']



class AudioCourseChapter(models.Model):  # for course ( maybe must has subscription ) ==> audio chapters
    title = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    audio = models.ForeignKey(AudioCourse, on_delete=models.CASCADE)
    start_time = models.CharField(max_length=10)
    create_date = models.DateTimeField(default=timezone.now, editable=False)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def start_sec(self):
        """Get seconds from start_time."""
        m, s = self.start_time.split(':')
        return int(m) * 60 + int(s)


class AudioWeekChapter(models.Model):  # for course ( maybe must has subscription ) ==> audio chapters
    title = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    audio = models.ForeignKey('AudioWeek', on_delete=models.CASCADE)
    start_time = models.CharField(max_length=10)
    create_date = models.DateTimeField(default=timezone.now, editable=False)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def start_sec(self):
        """Get seconds from start_time."""
        m, s = self.start_time.split(':')
        return int(m) * 60 + int(s)


class AudioArticleChapter(models.Model):  # for article ==> audio chapters
    title = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    audio = models.ForeignKey(AudioArticle, on_delete=models.CASCADE)
    start_time = models.CharField(max_length=10)
    create_date = models.DateTimeField(default=timezone.now, editable=False)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def start_sec(self):
        """Get seconds from start_time."""
        m, s = self.start_time.split(':')
        return int(m) * 60 + int(s)


class FileAttachment(models.Model):
    title = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    url = models.URLField(max_length=200, null=True)  # نگهداری آدرس فایل
    audio = models.ForeignKey(Audio, on_delete=models.CASCADE)  # کلید خارجی به مدل Audio
    create_date = models.DateTimeField(default=timezone.now, editable=False)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} / {self.audio.title}"

    class Meta:
        permissions = [("can_view_monetary_file", "Can view monetary file")]


class VideoAttachment(models.Model):
    title = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    url = models.URLField(max_length=200, null=True)
    audio = models.ForeignKey(Audio, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now, editable=False)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} / {self.audio.title}"

    class Meta:
        permissions = [("can_view_monetary_video", "Can view monetary video")]
