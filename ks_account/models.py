from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone

from kheylisadas import settings


class User(AbstractUser):
    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_CHOICES = (
        (GENDER_MALE, 'Male',),
        (GENDER_FEMALE, 'Female',),
    )
    mobile = models.CharField(max_length=11, null=False, blank=False)
    mobile_active_code = models.IntegerField(null=True, blank=True)
    is_delete = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='users', null=True, blank=True)
    email_active_code = models.IntegerField(null=True, blank=True)
    date_edited = models.DateTimeField(default=timezone.now)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birthday = models.DateTimeField(null=True, blank=True)
    presenting_code = models.CharField(max_length=10, null=True, blank=True)
    presenter = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    about_user = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    objects = UserManager()

    def __str__(self):
        return self.username


class ActivityLog(models.Model):
    LOGIN_SUCCESS = 1
    LOGIN_FAILED_INCORRECT_CAPTCHA = 2
    LOGIN_FAILED_INCORRECT_PASSWORD = 3
    SENT_ACTIVATION_SMS = 4
    SENT_RESET_PASSWORD_SMS = 5
    REGISTER_SUCCESS = 6
    INVALID_MOBILE_NUMBER = 7
    DUPLICATE_MOBILE_NUMBER = 8
    SMS_DELIVERY_FAILED = 9
    ACTIVATION_FAILED_INVALID_CODE = 10
    ACTIVATION_FAILED_EXPIRED_CODE = 11
    ACTIVATION_FAILED_USER_NOT_FOUND = 12
    REGISTER_FAILED_UNKNOWN = 13
    ACTIVATION_FAILED_UNKNOWN = 14
    SENT_ACTIVATION_SMS_VERIFIED = 15  # مورد جدید
    ACTIVATION_FAILED_INVALID_CODE_ENTERED = 16  # مورد جدید
    LOGIN_FAILED_USER_NOT_FOUND = 17  # مورد جدید

    TYPE_CHOICES = (
        (LOGIN_SUCCESS, 'ورود موفق'),
        (LOGIN_FAILED_INCORRECT_CAPTCHA, 'ورود ناموفق - تصویر امنیتی اشتباه'),
        (LOGIN_FAILED_INCORRECT_PASSWORD, 'ورود ناموفق - کلمه عبور اشتباه'),
        (SENT_ACTIVATION_SMS, 'ارسال پیامک فعالسازی'),
        (SENT_RESET_PASSWORD_SMS, 'ارسال پیامک بازیابی رمز عبور'),
        (REGISTER_SUCCESS, 'ثبت نام موفق'),
        (INVALID_MOBILE_NUMBER, 'شماره موبایل نامعتبر'),
        (DUPLICATE_MOBILE_NUMBER, 'شماره موبایل تکراری'),
        (SMS_DELIVERY_FAILED, 'ارسال پیامک فعالسازی ناموفق'),
        (ACTIVATION_FAILED_INVALID_CODE, 'کد فعالسازی نامعتبر'),
        (ACTIVATION_FAILED_EXPIRED_CODE, 'کد فعالسازی منقضی شده'),
        (ACTIVATION_FAILED_USER_NOT_FOUND, 'کاربر یافت نشد'),
        (REGISTER_FAILED_UNKNOWN, 'خطای ثبت نام ناشناخته'),
        (ACTIVATION_FAILED_UNKNOWN, 'خطای فعالسازی ناشناخته'),
        (SENT_ACTIVATION_SMS_VERIFIED, 'کد فعالسازی وارد شده'),  # مورد جدید
        (ACTIVATION_FAILED_INVALID_CODE_ENTERED, 'کد فعالسازی اشتباه وارد شده'),  # مورد جدید
        (LOGIN_FAILED_USER_NOT_FOUND, 'ورود ناموفق. کاربر یافت نشد.'),  # مورد جدید
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # null=True و blank=True اضافه شدند
    type = models.IntegerField(choices=TYPE_CHOICES, null=False, blank=False)
    ip = models.CharField(max_length=30, null=True, blank=True)
    create_date = models.DateTimeField(default=timezone.now)
    description = models.TextField(null=True)
