from datetime import datetime, timedelta

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

from ks_account.models import User
from utility.choices import PaymentStatus
from utility.faraz_sms import send_campaign_response_question_sms

from utility.utils import upload_plans_image_path


class Plan(models.Model):
    title = models.CharField(max_length=150)  # english
    name = models.CharField(max_length=150)  # farsi
    fake_price = models.IntegerField(null=True, blank=True)
    price = models.IntegerField(null=False, blank=False)
    off_price = models.IntegerField(null=True, blank=True)
    off = models.IntegerField(null=True, blank=True)
    duration = models.IntegerField(null=False, blank=False)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    is_recommended = models.BooleanField(default=False)
    short_description = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    description_rich = CKEditor5Field('Description', config_name='default', null=True, blank=True)
    slug = models.SlugField(default="", blank='True', null=True,
                            db_index=True)  # samsung galaxy s 20 => samsung-galaxy-s-20
    thumb = models.ImageField(upload_to=upload_plans_image_path, null=True, blank=True)
    image = models.ImageField(upload_to=upload_plans_image_path, null=True, blank=True)
    plan_gift = models.IntegerField(default=0, null=False, blank=False)
    courses = models.ManyToManyField('ks_course.Course', blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        # return f"/articles/{self.category_id}/{self.id}/{self.slug}"
        return reverse('plan_detail', args=[self.id, self.slug])

    @property
    def price_1000(self):
        return int(self.price / 1000)

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


class Campaign(models.Model):
    title = models.CharField(max_length=150)  # english
    name = models.CharField(max_length=150)  # farsi
    fake_price = models.IntegerField(null=True, blank=True)
    price = models.IntegerField(null=False, blank=False)
    off_price = models.IntegerField(null=True, blank=True)
    off = models.IntegerField(null=True, blank=True)
    duration = models.IntegerField(null=False, blank=False)
    is_active = models.BooleanField(default=False) # تا کاربران کمپین رو ببینند
    is_open = models.BooleanField(default=False) # تا کاربران بتونند بخرند مثلا 3 روز
    is_delete = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False) # تا افراد غیر از ادمین نتونند ببینند
    short_description = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    description_rich = CKEditor5Field('Description', config_name='default', null=True, blank=True)
    slug = models.SlugField(default="", blank='True', null=True,
                            db_index=True)  # samsung galaxy s 20 => samsung-galaxy-s-20
    thumb = models.ImageField(upload_to=upload_plans_image_path, null=True, blank=True)
    image = models.ImageField(upload_to=upload_plans_image_path, null=True, blank=True)
    banner_course = models.ImageField(upload_to=upload_plans_image_path, null=True, blank=True)
    description_course = models.TextField(null=True, blank=True)
    banner_chart = models.ImageField(upload_to=upload_plans_image_path, null=True, blank=True)
    description_chart = models.TextField(null=True, blank=True)
    banner_3 = models.ImageField(upload_to=upload_plans_image_path, null=True, blank=True)
    description_3 = models.TextField(null=True, blank=True)
    banner_podcast = models.ImageField(upload_to=upload_plans_image_path, null=True, blank=True)
    description_podcast = models.TextField(null=True, blank=True)
    campaign_gift = models.IntegerField(default=0, null=False, blank=False)
    courses = models.ManyToManyField('ks_course.Course', blank=True)

    class Meta:
        permissions = (
            ('fully_view_campaign', 'Can fully view campaign'),
        )
        get_latest_by = 'create_date'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        # return f"/articles/{self.category_id}/{self.id}/{self.slug}"
        return reverse('plan_detail', args=[self.id, self.slug])

    @property
    def price_1000(self):
        return int(self.price / 1000)

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


class Chart(models.Model):
    title = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True) # تا کاربران کمپین رو ببینند
    url = models.URLField(max_length=400, null=True, blank=True)  # نگهداری آدرس فایل
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    category = models.ForeignKey('ks_category.Category', on_delete=models.CASCADE)
    description_rich = CKEditor5Field('Description', config_name='default', null=True, blank=True)

    def __str__(self):
        return f'{self.name} - {self.campaign.name} - {self.category.name}'


class CampaignWeek(models.Model):
    title = models.CharField(max_length=150)  # english
    name = models.CharField(max_length=150)  # farsi
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    is_answered = models.BooleanField(default=False)
    short_description = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    description_rich = CKEditor5Field('Description', config_name='default', null=True, blank=True)
    slug = models.SlugField(default="", blank='True', null=True,
                            db_index=True)  # samsung galaxy s 20 => samsung-galaxy-s-20
    url = models.CharField(max_length=2083, null=True, blank=True)  # طول 2083 برای URL به طور عملی کافی است

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        # return f"/articles/{self.category_id}/{self.id}/{self.slug}"
        return reverse('plan_detail', args=[self.id, self.slug]) #todo: campaign_week detail


class CampaignQuestion(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=800)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    campaign_week = models.ForeignKey(CampaignWeek, on_delete=models.CASCADE)
    message = models.TextField(max_length=5000)
    create_date = models.DateTimeField(default=timezone.now)
    response = models.TextField(null=True, blank=True)
    is_read_by_admin = models.BooleanField(default=False)
    url = models.URLField(max_length=400, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.url:
            try:
                send_campaign_response_question_sms(self.user.mobile,
                                                    self.campaign_week.campaign.name,
                                                    self.campaign_week.name)
            except Exception as e:
                print("An error occurred while sending SMS:", e)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.campaign_week} / {self.user}"



class Payment(models.Model):
    SUBSCRIPTION = 1
    COURSE = 2
    CAMPAIGN = 3
    TYPE_CHOICES = (
        (SUBSCRIPTION, 'اشتراک',),
        (COURSE, 'دوره',),
        (CAMPAIGN, 'کمپین',),
    )
    CASH = 1
    ZARINPAL = 2
    GIFT = 3
    METHOD_TYPE_CHOICES = (
        (CASH, 'نقدی',),
        (ZARINPAL, 'آنلاین',),
        (GIFT, 'هدیه',),
    )
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    method = models.IntegerField(choices=METHOD_TYPE_CHOICES, null=True, blank=True,
                                 default=ZARINPAL)  # naghdi ya online (choice field)
    ref_code = models.CharField(default='0', max_length=20, null=False, blank=False)
    is_paid = models.BooleanField(default=False)
    price = models.IntegerField(default=0, null=False, blank=False)
    status = models.CharField(max_length=100, choices=PaymentStatus.CHOICES, null=True, blank=True)
    error = models.CharField(max_length=100, null=True, blank=True)
    type = models.IntegerField(choices=TYPE_CHOICES, null=True, blank=True)
    create_date = models.DateTimeField(default=timezone.now, null=False, blank=False)
    payment_date = models.DateTimeField(null=True, blank=True)

    @property
    def get_price(self):
        return int(self.price / 1000)

    def __str__(self):
        # return f"p:{self.price}-user:{self.user} at {self.payment_date} method {self.get_method_display()}"
        return f"مبلغ: {self.price} -کاربر:{self.user} زمان {self.payment_date} طریقه {self.get_method_display()}"


class Transaction(models.Model):
    BEFORE_PAYMENT = 1
    ERROR_BEFORE_PAYMENT = 2
    SUCCESS_PAYMENT = 3

    STATUS_CHOICES = (
        (BEFORE_PAYMENT, 'قبل از پرداخت',),
        (ERROR_BEFORE_PAYMENT, 'خطا - قبل از پرداخت',),
        (SUCCESS_PAYMENT, 'پرداخت موفق',),
    )

    # ایجاد دیکشنری برای نگهداری مقادیر
    STATUS_CODES = {
        "BEFORE_PAYMENT": BEFORE_PAYMENT,
        "ERROR_BEFORE_PAYMENT": ERROR_BEFORE_PAYMENT,
        "SUCCESS_PAYMENT": SUCCESS_PAYMENT,
    }
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True, blank=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True)
    create_date = models.DateTimeField(default=timezone.now, null=False, blank=False)
    try_date = models.DateTimeField(default=timezone.now, null=False, blank=False)
    start_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    in_process = models.BooleanField(default=False)
    status = models.IntegerField(choices=STATUS_CHOICES, null=True, blank=True, default=BEFORE_PAYMENT)
    gift_day = models.IntegerField(default=0, null=False, blank=False)
    info = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"کاربر: {self.user.__str__()} اشتراک: {self.plan.__str__()}"

    @property
    def is_expired_this(self):
        if self.end_date < timezone.now():
            self.is_expired = True
            # print("expired " + self.is_expired)
            self.save()
            return True
        # print("not expired")
        return False

    def calculate_expire_date(self):
        if self.plan:
            self.end_date = self.start_date.date() + timedelta(days=self.plan.duration) \
                            + timedelta(days=self.gift_day)

    def left_days(self):
        try:
            d = self.end_date - timezone.now()
            return d.days
        except:
            print("Something went wrong")
            return 0


@receiver(pre_save, sender=Transaction)
def my_callback(sender, instance, *args, **kwargs):
    instance.calculate_expire_date()


class CTransaction(models.Model):
    BEFORE_PAYMENT = 1
    ERROR_BEFORE_PAYMENT = 2
    SUCCESS_PAYMENT = 3

    STATUS_CHOICES = (
        (BEFORE_PAYMENT, 'قبل از پرداخت',),
        (ERROR_BEFORE_PAYMENT, 'خطا - قبل از پرداخت',),
        (SUCCESS_PAYMENT, 'پرداخت موفق',),
    )

    # ایجاد دیکشنری برای نگهداری مقادیر
    STATUS_CODES = {
        "BEFORE_PAYMENT": BEFORE_PAYMENT,
        "ERROR_BEFORE_PAYMENT": ERROR_BEFORE_PAYMENT,
        "SUCCESS_PAYMENT": SUCCESS_PAYMENT,
    }
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey('ks_category.Category', on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now, null=False, blank=False)
    try_date = models.DateTimeField(default=timezone.now, null=False, blank=False)
    start_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    in_process = models.BooleanField(default=False)
    status = models.IntegerField(choices=STATUS_CHOICES, null=True, blank=True, default=BEFORE_PAYMENT)
    gift_day = models.IntegerField(default=0, null=False, blank=False)
    info = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"کاربر: {self.user.__str__()} کمپین: {self.campaign.__str__()}"

    @property
    def is_expired_this(self):
        if self.end_date < timezone.now():
            self.is_expired = True
            # print("expired " + self.is_expired)
            self.save()
            return True
        # print("not expired")
        return False

    def calculate_expire_date(self):
        self.end_date = self.start_date.date() + timedelta(days=self.campaign.duration) \
                        + timedelta(days=self.gift_day)

    def left_days(self):
        try:
            d = self.end_date - timezone.now()
            return d.days
        except:
            print("Something went wrong")
            return 0


@receiver(pre_save, sender=CTransaction)
def my_callback(sender, instance, *args, **kwargs):
    instance.calculate_expire_date()


class GiftPlan(models.Model):
    code = models.CharField(max_length=10, unique=True, help_text="Enter the gift code")
    percentage = models.PositiveSmallIntegerField(help_text="Enter the discount percentage (e.g., 10 for 10%)")
    max = models.IntegerField(null=True, blank=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
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
