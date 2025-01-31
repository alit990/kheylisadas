import time

from django.contrib.auth.models import Group
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

import ks_audio
from ks_account.models import User
from ks_site.models import AgeCategory
from ks_subscription.models import Payment
from ks_tag.models import Tag
from utility.choices import KSChoices
from utility.utils import upload_course_image_path, group_course_name


# class CourseManager(models.Manager):
#     def get_audio_count(self):
#         audio_count = 0
#         sections_course = SectionCourse.objects.filter(course_id=self.id, is_active=True)
#         for section in sections_course:
#             audios = AudioCourse.objects.filter(section_course_id=section.id, is_active=True)
#             audio_count += audios.count()
#         return audio_count
#         return self.get_queryset().filter(is_active=True)

class Course(models.Model):
    title = models.CharField(max_length=150, null=True, blank=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    fake_price = models.IntegerField(null=True, blank=True)
    price = models.IntegerField(null=False, blank=False)
    off_price = models.IntegerField(null=True, blank=True)
    off = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    icon = models.CharField(default='A', max_length=10)
    thumb = models.ImageField(upload_to=upload_course_image_path, null=True, blank=True)
    image = models.ImageField(upload_to=upload_course_image_path, null=False, blank=False)
    alt_image = models.TextField(null=True, blank=True, max_length=100)
    description = models.TextField(null=True)
    create_date = models.DateTimeField(default=timezone.now, editable=False)
    slug = models.SlugField(default="", blank='True', null=True,
                            db_index=True)  # samsung galaxy s 20 => samsung-galaxy-s-20
    tags = models.ManyToManyField(Tag, blank=True)
    age_category = models.ForeignKey(AgeCategory, on_delete=models.CASCADE, null=True, blank=True)
    has_practice = models.BooleanField(default=False)
    last_update = models.DateTimeField(default=timezone.now, editable=True)
    fake_visit_count = models.IntegerField(default=5)
    fake_students_count = models.IntegerField(default=25)
    fake_like_count = models.IntegerField(default=5)
    fake_dislike_count = models.IntegerField(default=5)

    class Meta:
        permissions = (
            ('fully_view_course', 'Can fully view course'),
        )
        get_latest_by = 'create_date'


    def get_absolute_url(self):
        return reverse('course_detail', args=[self.id, self.slug])

    def get_absolute_url_price(self):
        return reverse('course_price_detail', args=[self.id, self.slug])

    @property
    def audio_count(self):
        audio_count = 0
        sections_course = SectionCourse.objects.filter(course_id=self.id, is_active=True)
        for section in sections_course:
            audio_count += section.section_audio_count
        return audio_count

    @property
    def audios_duration(self):
        duration = timezone.timedelta(0)
        for section in SectionCourse.objects.filter(course_id=self.id, is_active=True):
            duration += section.section_audio_duration
        # print(type(duration))
        return duration

    @property
    def students(self):
        return Group.objects.filter(name=group_course_name(self.title)).count()

    def price_1000(self):
        return int(self.price / 1000)

    def fake_price_1000(self):
        if self.fake_price:
            return int(self.fake_price / 1000)
        else:
            return 0

    def price_off_1000(self):
        return int(self.price / 1000)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    # class Meta:
    #     verbose_name = 'فصل دسته'
    #     verbose_name_plural = 'فصل دسته ها'

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.set_off_price = kwargs.get('set_off_price', list)
        self.off_price = None

    @property
    def set_off_price(self):
        return self.off_price

    @set_off_price.setter
    def set_off_price(self, values):  # 0 is percent and 1 is max
        percent, max_off = values
        off = self.price * percent / 100
        if off > max_off:
            off = max_off

        if int(self.price - off) < 0:
            self.off_price = 0
            self.off = int(self.price)
        else:
            self.off = int(off)
            self.off_price = int(self.price - off)


class SectionCourse(models.Model):
    title = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} / {self.course}"

    @property
    def section_audio_count(self):
        return ks_audio.models.AudioCourse.objects.filter(section_course_id=self.id, is_active=True).count()

    @property
    def section_audio_duration(self):
        duration = timezone.timedelta(0)
        for audio in ks_audio.models.AudioCourse.objects.filter(section_course_id=self.id, is_active=True):
            duration += audio.duration
        return duration


class CourseComment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    parent = models.ForeignKey('CourseComment', null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now)
    text = models.TextField()
    is_allowed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)


class CourseVisit(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    ip = models.CharField(max_length=30)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.course.title} / {self.ip}'


class TransactionCourse(models.Model):
    BEFORE_PAYMENT = 1
    ERROR_BEFORE_PAYMENT = 2
    SUCCESS_PAYMENT = 3
    STATUS_CHOICES = (
        (BEFORE_PAYMENT, 'قبل از پرداخت',),
        (ERROR_BEFORE_PAYMENT, 'خطا - قبل از پرداخت',),
        (SUCCESS_PAYMENT, 'پرداخت موفق',),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True)
    create_date = models.DateTimeField(default=timezone.now, null=False, blank=False)
    try_date = models.DateTimeField(default=timezone.now, null=False, blank=False)
    # start_date = models.DateTimeField(null=True, blank=True)
    # end_date = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    in_process = models.BooleanField(default=False)
    status = models.IntegerField(choices=STATUS_CHOICES, null=True, blank=True, default=1)
    info = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"کاربر: {self.user.__str__()} دوره: {self.course.__str__()}"


class GiftCourse(models.Model):
    code = models.CharField(max_length=10, unique=True, help_text="Enter the gift code")
    percentage = models.PositiveSmallIntegerField(help_text="Enter the discount percentage (e.g., 10 for 10%)")
    max = models.IntegerField(null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_expired = models.BooleanField(default=False)
    start_date = models.DateField(default=timezone.now, null=True, blank=True,
                                  help_text="Enter the start date of the discount code")
    end_date = models.DateField(null=True, blank=True, help_text="Enter the end date of the discount code")

    def __str__(self):
        return self.code

    @property
    def is_expired_this(self):
        if self.end_date < timezone.now():
            self.is_expired = True
            self.save()
            return True
        return False
