import random
from datetime import timedelta

from django.db import models
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

import ks_audio
from ks_account.models import User
from ks_audio.models import Audio, AudioWeek
from ks_site.models import AgeCategory
from ks_tag.models import Tag
from utility.choices import KSChoices
from utility.utils import upload_category_image_path, upload_week_image_path, get_random_number


# Create your models here.
class CCDetailManager(models.Manager):
    def get_active_products(self):
        return self.get_queryset().filter(is_active=True)

    def get_details_by_category(self, category_id):
        return self.get_queryset().filter(category_id=category_id, is_active=True)

    def get_details_by_category_chapter(self, category_id, chapter_id):
        # return self.get_queryset().filter(category_id=category_id, chapter_id=chapter_id, is_active=True).first()
        return get_object_or_404(CCDetail, category_id=category_id, chapter_id=chapter_id, is_active=True)

    def get_by_id(self, ccdetail_id):
        qs = self.get_queryset().filter(id=ccdetail_id)
        if qs.count() == 1:
            return qs.first()
        else:
            return None

    # def search(self, query):
    #     lookup = (
    #             Q(title__icontains=query) |
    #             Q(description__icontains=query) |
    #             Q(tag__title__icontains=query)
    #     )
    #     return self.get_queryset().filter(lookup, active=True).distinct()


class Chapter(models.Model):
    title = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    # thumb = models.ImageField(upload_to=upload_category_image_path, null=True, blank=True)
    image = models.ImageField(upload_to=upload_category_image_path, null=True, blank=True)
    alt_image = models.TextField(null=True, blank=True, max_length=100)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    create_date = models.DateTimeField(default=timezone.now, editable=False)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(default="", null=False, blank=True,
                            db_index=True)  # samsung galaxy s 20 => samsung-galaxy-s-20

    def get_absolute_url(self):
        return reverse('chapter-detail', args=[self.id, self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def get_audio_url(self, category_id):
        ccdetail: CCDetail = CCDetail.objects.filter(category_id=category_id, chapter_id=self.id).first()
        return ccdetail.audio_url

    def __str__(self):
        return self.name


class Category(models.Model):
    title = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    age_range = models.CharField(default='2 تا 3 ماهگی', max_length=30)
    thumb = models.ImageField(upload_to=upload_category_image_path, null=True, blank=True)
    alt_thumb_image = models.TextField(null=True, blank=True, max_length=100)
    image = models.ImageField(upload_to=upload_category_image_path, null=True, blank=True)
    alt_image = models.TextField(null=True, blank=True, max_length=100)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    create_date = models.DateTimeField(default=timezone.now, editable=False)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(default="", blank='True', null=True,
                            db_index=True)  # samsung galaxy s 20 => samsung-galaxy-s-20
    chapters = models.ManyToManyField(Chapter, blank=True)
    is_disabled = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('category-detail', args=[self.id, self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def audio_category_count(self):
        count = 0
        for ccdetail in CCDetail.objects.filter(category_id=self.id, is_active=True):
            count += ccdetail.audio_count
        return count


class CCDetail(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    title = models.CharField(max_length=150, null=True, blank=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    create_date = models.DateTimeField(default=timezone.now, editable=False)
    # thumb = models.ImageField(upload_to=upload_category_image_path, null=True, blank=True)
    image = models.ImageField(upload_to=upload_category_image_path, null=True, blank=True)
    alt_image = models.TextField(null=True, blank=True, max_length=100)
    slug = models.SlugField(default="", blank='True', null=True,
                            db_index=True)  # samsung galaxy s 20 => samsung-galaxy-s-20
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    age_category = models.ForeignKey(AgeCategory, on_delete=models.CASCADE, null=True, blank=True)
    has_practice = models.BooleanField(default=False)
    audio_url = models.URLField(max_length=200, null=True, blank=True)
    last_update = models.DateTimeField(default=timezone.now, editable=True)
    fake_visit_count = models.IntegerField(default=get_random_number(10, 30))
    fake_like_count = models.IntegerField(default=get_random_number(8, 23))
    fake_dislike_count = models.IntegerField(default=get_random_number(1, 7))

    objects = CCDetailManager()

    def save(self, *args, **kwargs):
        self.title = f"{self.category.title}: {self.chapter.title}"
        self.name = f"{self.category.name}: {self.chapter.name}"
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def audio_count(self):
        count = 0
        for section in Section.objects.filter(ccdetail_id=self.id, is_active=True):
            count += section.section_audio_count
        return count

    @property
    def audios_duration(self):
        duration = timezone.timedelta(0)
        for section in Section.objects.filter(ccdetail_id=self.id, is_active=True):
            duration += section.section_audio_duration
        return duration

    def __str__(self):
        return self.name


class Section(models.Model):
    title = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    create_date = models.DateTimeField(default=timezone.now, editable=False)
    ccdetail = models.ForeignKey(CCDetail, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} / {self.ccdetail}"

    @property
    def section_audio_count(self):
        return ks_audio.models.Audio.objects.filter(section_id=self.id, is_active=True).count()

    @property
    def section_audio_duration(self):
        duration = timezone.timedelta(0)
        for audio in ks_audio.models.Audio.objects.filter(section_id=self.id, is_active=True):
            audio_duration = audio.duration if audio.duration is not None else timedelta(0)
            duration += audio_duration
        return duration


class Week(models.Model):
    title = models.CharField(max_length=150, null=True, blank=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    create_date = models.DateTimeField(default=timezone.now, editable=False)
    thumb = models.ImageField(upload_to=upload_week_image_path, null=True, blank=True)
    alt_thumb_image = models.TextField(null=True, blank=True, max_length=100)
    image = models.ImageField(upload_to=upload_week_image_path, null=True, blank=True)
    alt_image = models.TextField(null=True, blank=True, max_length=100)
    slug = models.SlugField(default="", blank='True', null=True,
                            db_index=True)  # samsung galaxy s 20 => samsung-galaxy-s-20
    description = models.TextField(null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    age_category = models.ForeignKey(AgeCategory, on_delete=models.CASCADE, null=True, blank=True)
    has_practice = models.BooleanField(default=False)
    last_update = models.DateTimeField(default=timezone.now, editable=True)
    fake_visit_count = models.IntegerField(default=5)
    fake_like_count = models.IntegerField(default=5)
    fake_dislike_count = models.IntegerField(default=5)
    audio_url = models.URLField(max_length=200, null=True)

    objects = CCDetailManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def audio_count(self):
        audio_count = 0
        for section in SectionWeek.objects.filter(week_id=self.id, is_active=True):
            audio_count += section.section_audio_count
        return audio_count

    @property
    def audios_duration(self):
        duration = timezone.timedelta(0)
        for section in SectionWeek.objects.filter(week_id=self.id, is_active=True):
            duration += section.section_audio_duration
        return duration


class CCDetailComment(models.Model):
    ccdetail = models.ForeignKey(CCDetail, on_delete=models.CASCADE)
    parent = models.ForeignKey('CCDetailComment', null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now)
    text = models.TextField()
    is_allowed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)


class AudioComment(models.Model):
    audio = models.ForeignKey('ks_audio.Audio', on_delete=models.CASCADE)
    parent = models.ForeignKey('AudioComment', null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now)
    text = models.TextField()
    is_allowed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)


class AudioWeekComment(models.Model):
    audioweek = models.ForeignKey('ks_audio.AudioWeek', on_delete=models.CASCADE)
    parent = models.ForeignKey('AudioWeekComment', null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now)
    text = models.TextField()
    is_allowed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)


class WeekComment(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    parent = models.ForeignKey('WeekComment', null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now)
    text = models.TextField()
    is_allowed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)


class SectionWeek(models.Model):
    title = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    create_date = models.DateTimeField(default=timezone.now, editable=False)
    description = models.TextField(null=True, blank=True)
    week = models.ForeignKey(Week, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} / {self.week}"

    @property
    def section_audio_count(self):
        return ks_audio.models.AudioWeek.objects.filter(section_week=self.id, is_active=True).count()

    @property
    def section_audio_duration(self):
        duration = timezone.timedelta(0)
        for audio in ks_audio.models.AudioWeek.objects.filter(section_week_id=self.id, is_active=True):
            duration += audio.duration
        return duration


class CCDetailVisit(models.Model):
    ccdetail = models.ForeignKey('CCDetail', on_delete=models.CASCADE)
    ip = models.CharField(max_length=30)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f'{self.ccdetail.title} / {self.ip}'


class WeekVisit(models.Model):
    week = models.ForeignKey('Week', on_delete=models.CASCADE)
    ip = models.CharField(max_length=30)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f'{self.week.title} / {self.ip}'
