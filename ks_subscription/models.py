from datetime import datetime, timedelta

from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from ks_account.models import User
from utility.choices import PaymentStatus

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
    description_rich = RichTextUploadingField(null=True, blank=True)
    slug = models.SlugField(default="", blank='True', null=True,
                            db_index=True)  # samsung galaxy s 20 => samsung-galaxy-s-20
    icon = models.CharField(default='A', max_length=10)
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


class Payment(models.Model):
    SUBSCRIPTION = 1
    COURSE = 2
    TYPE_CHOICES = (
        (SUBSCRIPTION, 'اشتراک',),
        (COURSE, 'دوره',),
    )
    CASH = 1
    ZARINPAL = 2
    GIFT = 3
    METHOD_TYPE_CHOICES = (
        (CASH, 'نقدی',),
        (ZARINPAL, 'آنلاین',),
        (GIFT, 'هدیه',),
    )
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
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

    # def save(self, *args, **kwargs):
    # self.start_date = datetime.datetime.now().time()
    # if str(self.start_date) != '':
    #     self.end_date = self.start_date + datetime.timedelta(days=self.plan.duration) \
    # + datetime.timedelta(days=self.gift_day)

    # super().save(*args, **kwargs)

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
