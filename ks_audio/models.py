from django.db import models
from django.utils import timezone

from ks_account.models import User
from ks_category.models import Section, SectionWeek, CCDetail, Week
from ks_course.models import SectionCourse
from utility.choices import KSChoices
from utility.utils import upload_audio_image_path, upload_audio_file_path, upload_audio_course_file_path


class Audio(models.Model):  # for category chapter ( ccdetail )
    title = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    # icon = models.CharField(default='A', max_length=10)
    # thumb = models.ImageField(upload_to=upload_audio_image_path, null=True, blank=True)
    # image = models.ImageField(upload_to=upload_audio_image_path, null=True, blank=True)
    # file = models.FileField(upload_to=upload_audio_file_path, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    is_lock = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now, editable=False)
    type = models.IntegerField(choices=KSChoices.CHOICES_AUDIO_TYPE, null=False, blank=False)
    parent = models.ForeignKey('Audio', on_delete=models.DO_NOTHING, null=True, blank=True)
    url = models.URLField(max_length=200, null=True)
    duration = models.DurationField(null=True, blank=True)
    fake_played_count = models.IntegerField(default=5)
    fake_like_count = models.IntegerField(default=5)
    fake_dislike_count = models.IntegerField(default=5)

    def __str__(self):
        return f"{self.name} / {self.section} / {self.type}"

    class Meta:
        permissions = [("can_view_monetary_audio", "Can view monetary audio")]


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

    def __str__(self):
        return f"{self.name} / {self.section_course}"


class AudioWeek(models.Model):  # for week
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
    section_week = models.ForeignKey(SectionWeek, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now, editable=False)
    type = models.IntegerField(choices=KSChoices.CHOICES_AUDIO_TYPE, null=False, blank=False)
    parent = models.ForeignKey('AudioWeek', on_delete=models.DO_NOTHING, null=True, blank=True)
    url = models.URLField(max_length=200, null=True)
    duration = models.DurationField(null=True, blank=True)
    fake_played_count = models.IntegerField(default=5)
    fake_like_count = models.IntegerField(default=5)
    fake_dislike_count = models.IntegerField(default=5)

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


class AudioChapter(models.Model):  # for category chapter ( ccdetail ) ==> audio chapters
    title = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    audio = models.ForeignKey(Audio, on_delete=models.CASCADE)
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
    audio = models.ForeignKey(AudioWeek, on_delete=models.CASCADE)
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
