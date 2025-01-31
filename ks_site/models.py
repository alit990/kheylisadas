from django.db import models
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field

from ks_account.models import User
from utility.faraz_sms import send_contact_response_sms
from utility.utils import upload_site_files_path, upload_avatar_image_path


class SiteSetting(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)
    site_name = models.CharField(max_length=200)
    site_url = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    telegram = models.CharField(max_length=200, null=True, blank=True)
    eitaa = models.CharField(max_length=200, null=True, blank=True)
    instagram = models.CharField(max_length=200, null=True, blank=True)
    copy_right = models.TextField()
    page_message = models.TextField(default="", null=False, blank=False)
    about_us_rich = CKEditor5Field('about_us', config_name='default', null=True, blank=True)
    plan_description_rich = CKEditor5Field('plan_description', config_name='default', null=True, blank=True)
    site_logo1 = models.ImageField(upload_to=upload_site_files_path, null=False, blank=False)
    site_logo2 = models.ImageField(upload_to=upload_site_files_path, null=False, blank=False)
    site_logo3 = models.ImageField(upload_to=upload_site_files_path, null=False, blank=False)
    site_logo_footer = models.ImageField(upload_to=upload_site_files_path, null=True, blank=True)
    is_main_setting = models.BooleanField()
    courses_is_disabled = models.BooleanField(default=True)
    articles_is_disabled = models.BooleanField(default=True)
    weeks_is_disabled = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)  # فیلد برای حالت به‌روزرسانی

    def __str__(self):
        return self.title


class AccountSetting(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)
    title_ks = models.CharField(max_length=200, null=True, blank=True)
    login_text = models.TextField()
    mobile_activation_text = models.TextField()
    register_username_text = models.TextField()
    logo_ks = models.ImageField(upload_to=upload_site_files_path, null=False, blank=False)
    icon_ks = models.ImageField(upload_to=upload_site_files_path, null=False, blank=False)
    is_main_setting = models.BooleanField()

    def __str__(self):
        return self.title


class Reference(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(upload_to=upload_site_files_path, null=False, blank=False)
    alt = models.CharField(max_length=200, null=True, blank=True)
    description = models.CharField(max_length=400, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Avatar(models.Model):
    avatar = models.ImageField(upload_to=upload_avatar_image_path, null=True, blank=True)
    avatar_admin = models.ImageField(upload_to=upload_avatar_image_path, null=True, blank=True)
    avatar_staff = models.ImageField(upload_to=upload_avatar_image_path, null=True, blank=True)
    is_main = models.BooleanField()


class ContactUs(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=800)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(max_length=5000)
    create_date = models.DateTimeField(default=timezone.now)
    response = models.TextField(null=True, blank=True)
    is_read_by_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} / {self.user}"

    def save(self, *args, **kwargs):
        old_instance = ContactUs.objects.filter(pk=self.pk).first()
        super(ContactUs, self).save(*args, **kwargs)
        if self.is_read_by_admin and self.response and (
                not old_instance or not old_instance.is_read_by_admin or not old_instance.response):
            try:
                send_contact_response_sms(self.user.mobile, self.id)
            except Exception as e:
                print("An error occurred while sending response SMS:", e)


class FrequentQuestionCategory(models.Model):
    title = models.CharField(max_length=150, null=True, blank=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    create_date = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return self.name


class FrequentQuestion(models.Model):
    category = models.ForeignKey(FrequentQuestionCategory, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=150, null=True, blank=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    question = models.TextField(null=False)
    answer = models.TextField(null=False)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    create_date = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return self.question


class AgeCategory(models.Model):
    title = models.CharField(max_length=800)
    name = models.CharField(max_length=800)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.name
