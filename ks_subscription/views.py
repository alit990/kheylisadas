from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, OperationalError

from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, DetailView, FormView
from django.views.generic.edit import FormMixin
from guardian.shortcuts import assign_perm, remove_perm

from kheylisadas import settings
from ks_account.decorators import signup_required
from ks_account.models import User
from ks_audio.models import Audio, AudioWeek, AudioCourse
from ks_category.models import Category
from ks_course.models import Course, SectionCourse
from ks_site.forms import ContactUsForm
from ks_site.models import SiteSetting
from ks_subscription.forms import GiftCodeForm, CategoryChoiceForm, CampaignQuestionForm
from ks_subscription.models import Plan, Payment, Transaction, GiftPlan, CTransaction, Campaign, Chart, CampaignWeek, \
    CampaignQuestion
import time
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse, HttpResponse, HttpResponseForbidden
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, render
import requests
import json

from utility.choices import PaymentStatus
from utility.faraz_sms import send_new_subscription_sms, send_try_pay_sms, send_new_campaign_sms, standard_number, \
    send_contact_us_sms
from utility.utils import group_subscription_name, codename_audio_week_perm, codename_audio_perm, group_course_name

if settings.SANDBOX:
    sandbox = 'sandbox'
else:
    sandbox = 'www'
MERCHANT = settings.MERCHANT
ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"
description = "نهایی کردن خرید اشتراک خیلی ساده ست"  # Required
email = ''  # Optional
mobile = ''  # Optional


# todo: Important: need to edit for real server.
# CallbackURL = 'http://127.0.0.1:8000/subscription/verify-payment/'
# CallbackURL = reverse_lazy('verify_payment')


class PlansList(ListView):
    template_name = 'plans.html'
    paginate_by = 3

    # context_object_name = 'plans'
    def dispatch(self, request, *args, **kwargs):
        # بررسی وجود کمپین فعال
        active_campaign = Campaign.objects.filter(is_active=True, is_open=True, is_published=True).first()
        if active_campaign:
            # اگر کمپین فعال وجود داشت، کاربر را به CampaignDetailView هدایت کنید
            return redirect(reverse('campaign_detail', kwargs={'pk': active_campaign.pk, 'slug': active_campaign.slug}))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Plan.objects.filter(is_active=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PlansList, self).get_context_data()
        setting: SiteSetting = SiteSetting.objects.filter(is_main_setting=True).first()
        context['site_setting'] = setting
        return context


# @method_decorator(login_required, name='dispatch')
@method_decorator(signup_required, name='dispatch')
class PlanDetailView(FormMixin, DetailView):
    model = Plan
    template_name = 'plan_detail.html'
    form_class = GiftCodeForm

    def get_success_url(self):
        return reverse('plan_detail', kwargs={'pk': self.object.pk, 'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        context = super(PlanDetailView, self).get_context_data(**kwargs)
        # context['form'] = self.get_form()
        context['gift_form'] = self.get_form()
        # plan: Plan = kwargs.get('object')

        user_id = self.request.user.id
        current_user: User = User.objects.filter(id=user_id, is_active=True).first()

        # permission group for subscription
        has_perm = current_user.groups.filter(name=group_subscription_name()).exists()
        if Transaction.objects.filter(user_id=current_user.id, is_paid=True, is_expired=False).exists() and has_perm:
            transaction: Transaction = Transaction.objects.filter(
                user_id=current_user.id, is_paid=True, is_expired=False).first()
            if transaction.is_expired_this:
                content_type_audio = ContentType.objects.get_for_model(Audio)
                perm_view_audio, created = Permission.objects.get_or_create(codename=codename_audio_perm(),
                                                                            content_type=content_type_audio)
                content_type_audio_week = ContentType.objects.get_for_model(AudioWeek)
                perm_view_audio_week, created = Permission.objects.get_or_create(
                    codename=codename_audio_week_perm(),
                    content_type=content_type_audio_week)
                plan_group, plan_created = Group.objects.get_or_create(name=group_subscription_name())
                if plan_created:
                    plan_group.permissions.add(perm_view_audio, perm_view_audio_week)
                current_user.groups.remove(plan_group)
                has_perm = False
            context['transaction'] = transaction
        context['has_perm'] = has_perm
        context['gift_code'] = 'n'
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        print(form.cleaned_data)
        # context = self.get_context_data()
        context = super(PlanDetailView, self).get_context_data()
        context['gift_form'] = form
        code = form.cleaned_data.get('code')
        plan = self.get_object()
        try:
            gift_plan = GiftPlan.objects.filter(code__iexact=code).first()
            if gift_plan:
                plan.set_off_price = (gift_plan.percentage, gift_plan.max)
                # plan.save()
                context['code_valid'] = f"کد تخفیف {code} اعمال شد "
                context['plan'] = plan
                context['gift_code'] = gift_plan.code
            else:
                form.add_error(field='code', error=' نامعتبر ')
                # form.add_error(field='code', error='invalid')
                return self.form_invalid(form)
        except ObjectDoesNotExist:
            form.add_error(field='code', error=' نامعتبر ')
            context['gift_code'] = 'n'
            return self.form_invalid(form)

        # return super(AuthorDetail, self).form_valid(form)
        return self.render_to_response(context)

    def form_invalid(self, form):
        # This method is called when valid form data has NOT been POSTed
        # It should return a different HttpResponse
        context = self.get_context_data()
        context['gift_form'] = form
        return self.render_to_response(context)
@method_decorator(signup_required, name='dispatch')
class CampaignDetailView(FormMixin, DetailView):
    model = Campaign
    template_name = 'campaign_detail.html'
    form_class = CategoryChoiceForm

    # def get_success_url(self):
    #     return reverse('plan_detail', kwargs={'pk': self.object.pk, 'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        context = super(CampaignDetailView, self).get_context_data(**kwargs)
        # context['form'] = self.get_form()
        campaign = self.object
        courses = campaign.courses.all()
        course_audio_list = []
        course_name = ""
        for course in courses:
            course_name = course.name
            sections = SectionCourse.objects.filter(course=course, is_active=True)
            for section in sections:
                audios = AudioCourse.objects.filter(section_course=section, is_active=True)
                for audio in audios:
                    course_audio_list.append({
                        'audio_name': audio.name,
                        'audio_url': audio.url,
                    })
        context['course_audio_list'] = course_audio_list
        context['course_name'] = course_name


        user_id = self.request.user.id
        current_user: User = User.objects.filter(id=user_id, is_active=True).first()

        # permission group for campaign
        has_campaign = False
        if self.request.user.is_authenticated:
            current_user: User = self.request.user
            user_id = current_user.id
            has_campaign = current_user.has_perm('fully_view_campaign', campaign)  # guardian library
            # has_campaign = has_perm(self.request.user, 'fully_view_campaign', campaign)  # guardian library


        if CTransaction.objects.filter(user_id=current_user.id, is_paid=True, is_expired=False).exists() and has_campaign:
            c_transaction = CTransaction.objects.filter(
                user_id=current_user.id, is_paid=True, is_expired=False).first()
            if c_transaction.is_expired_this:
                try:
                    remove_perm('fully_view_campaign', current_user, campaign)
                    # سایر عملیات مربوط به انقضای اشتراک
                except Campaign.DoesNotExist:
                    # مدیریت خطای عدم وجود Campaign
                    pass
                has_campaign = False
            # context['c_transaction'] = c_transaction
            user_chart = Chart.objects.filter(campaign_id=campaign.id, is_active=True,
                                              category_id=c_transaction.category.id).first()
            context['user_chart'] = user_chart
        context['has_campaign'] = has_campaign
        charts = Chart.objects.filter(campaign_id=campaign.id, is_active=True)
        context['charts'] = charts


        has_perm = current_user.groups.filter(name=group_subscription_name()).exists()
        if Transaction.objects.filter(user_id=current_user.id, is_paid=True, is_expired=False).exists() and has_perm:
            transaction: Transaction = Transaction.objects.filter(
                user_id=current_user.id, is_paid=True, is_expired=False).first()
            if transaction.is_expired_this:
                content_type_audio = ContentType.objects.get_for_model(Audio)
                perm_view_audio, created = Permission.objects.get_or_create(codename=codename_audio_perm(),
                                                                            content_type=content_type_audio)
                content_type_audio_week = ContentType.objects.get_for_model(AudioWeek)
                perm_view_audio_week, created = Permission.objects.get_or_create(
                    codename=codename_audio_week_perm(),
                    content_type=content_type_audio_week)
                plan_group, plan_created = Group.objects.get_or_create(name=group_subscription_name())
                if plan_created:
                    plan_group.permissions.add(perm_view_audio, perm_view_audio_week)
                current_user.groups.remove(plan_group)
                has_perm = False
            context['transaction'] = transaction
        context['has_perm'] = has_perm
        campaign_weeks = CampaignWeek.objects.filter(is_active=True, campaign=campaign)
        context['campaign_weeks'] = campaign_weeks
        # بازیابی دسته‌بندی‌های مرتبط با کمپین
        categories = Category.objects.filter(chart__campaign=campaign)
        context['category_form'] = CategoryChoiceForm(categories=categories)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        selected_category = form.cleaned_data['category']
        campaign = self.object
        chart = Chart.objects.filter(campaign=campaign, category=selected_category).first()
        if chart:
            url = chart.url
            context = {'selected_category': selected_category, 'url': url, 'campaign': campaign}
            return render(self.request, self.template_name, context)
        else:
            context = {'selected_category': selected_category, 'url': None, 'campaign': campaign}
            return render(self.request, self.template_name, context)

    def form_invalid(self, form):
        context = self.get_context_data()
        context['category_form'] = form
        return self.render_to_response(context)

class CampaignQuestionDetailView(View):
    def get(self, request, *args, **kwargs):
        user_id = self.request.user.id
        campaign_id = kwargs['campaign_id']
        campaign_week_id = kwargs['campaign_week_id']
        campaign = Campaign.objects.filter(is_active=True, id=campaign_id).first()
        campaign_week = CampaignWeek.objects.filter(is_active=True, id=campaign_week_id).first()
        context = {}
        # permission group for campaign
        has_campaign = False
        current_user: User = self.request.user
        user_id = current_user.id
        has_campaign = current_user.has_perm('fully_view_campaign', campaign)  # guardian library

        if has_campaign:
            exists_question = CampaignQuestion.objects.filter(user_id=user_id, campaign_week=campaign_week).exists()
            if exists_question:
                context = {
                    'question': CampaignQuestion.objects.filter(user_id=user_id, campaign_week=campaign_week).first(),
                    'campaign': campaign,
                    'campaign_week': campaign_week,
                    'form': None,
                    'has_campaign': has_campaign
                }
                return render(request, 'campaign_question_detail.html', context)
            else:
                initial_dict = {
                    "mobile": current_user.mobile
                }
                contact_us_form = CampaignQuestionForm(request.POST or None, initial=initial_dict)
                context = {
                    'campaign': campaign,
                    'campaign_week': campaign_week,
                    'form': contact_us_form,
                    'has_campaign': has_campaign,
                }
                return render(request, 'campaign_question_detail.html', context)
        else:
            messages.error(request, "شما دسترسی لازم برای این کمپین را ندارید.")
            return redirect('error_page')  # به صفحه خطا هدایت کنید

    def post(self, request, *args, **kwargs):
        print("post register view")
        campaign_id = kwargs.get('campaign_id')
        campaign_week_id = kwargs.get('campaign_week_id')
        user = request.user
        campaign = Campaign.objects.filter(is_active=True, id=campaign_id).first()
        campaign_week = CampaignWeek.objects.filter(is_active=True, id=campaign_week_id).first()
        exists_question = CampaignQuestion.objects.filter(user=user, campaign_week=campaign_week).exists()
        form = CampaignQuestionForm(request.POST)
        if form.is_valid():
            mobile = form.cleaned_data.get('mobile')
            title = form.cleaned_data.get('title')
            message = form.cleaned_data.get('message')

            # ذخیره سوال
            campaign_question = CampaignQuestion.objects.create(
                user=user,
                title=title,
                message=message,
                campaign_week=campaign_week
            )
            try:
                send_contact_us_sms(mobile, campaign_question.id)
            except Exception as e:
                print("An error occurred while sending SMS:", e)
            # messages.success(request, 'پیام شما با موفقیت ارسال شد.')
            # بازگشت اطلاعات موفقیت
            context = {
                    'form': None,
                    'question': campaign_question,
                    'campaign': campaign,
                    'campaign_week': campaign_week,
                    'success': "پیام شما با موفقیت ارسال شد."
                }
            return render(request, 'campaign_question_detail.html', context)

        context = {
            'form': form,
            'campaign': campaign,
            'campaign_week': campaign_week,
            'errors': form.errors
        }

        return render(request, 'campaign_question_detail.html', context)

@login_required
def cancel_pending_payments(request: HttpRequest):
    current_user: User = request.user
    # Mark all in-process transactions as not in process
    for transaction in Transaction.objects.filter(user_id=current_user.id, in_process=True):
        transaction.in_process = False
        transaction.save()

    for c_transaction in CTransaction.objects.filter(user_id=current_user.id, in_process=True):
        c_transaction.in_process = False
        c_transaction.save()

    # Redirect to the payment page
    return redirect('plans_list')  # یا هر صفحه‌ای که کاربر می‌تواند مجددا پرداخت را آغاز کند


@login_required
def plan_free_gift(request: HttpRequest, *args, **kwargs):
    context = {}
    current_user: User = request.user
    plan_id = kwargs['plan_id']
    code = kwargs['code']
    gift_plan = GiftPlan.objects.filter(code__iexact=code).first()
    plan = Plan.objects.filter(id=plan_id).first()
    if gift_plan:
        plan.set_off_price = (gift_plan.percentage, gift_plan.max)
        # plan.save()
        if plan.off_price == 0:
            # permission group for subscription
            has_perm = current_user.groups.filter(name=group_subscription_name()).exists()
            if Transaction.objects.filter(user_id=current_user.id, is_paid=True,
                                          is_expired=False).exists() and has_perm:
                transaction = Transaction.objects.filter(
                    user_id=current_user.id, is_paid=True, is_expired=False).first()
                if transaction.is_expired_this:
                    content_type_audio = ContentType.objects.get_for_model(Audio)
                    perm_view_audio, created = Permission.objects.get_or_create(codename=codename_audio_perm(),
                                                                                content_type=content_type_audio)
                    content_type_audio_week = ContentType.objects.get_for_model(AudioWeek)
                    perm_view_audio_week, created = Permission.objects.get_or_create(
                        codename=codename_audio_week_perm(),
                        content_type=content_type_audio_week)
                    plan_group, plan_created = Group.objects.get_or_create(name=group_subscription_name())
                    if plan_created:
                        plan_group.permissions.add(perm_view_audio, perm_view_audio_week)
                    current_user.groups.remove(plan_group)
                    has_perm = False
            if has_perm:
                messages.error(request, 'متاسفانه در تخصیص اشتراک رایگان به شما خطایی رخ داده است. '
                                        'ظاهرا شما درحال حاضر یک اشتراک فعال دارید. ')
                return redirect('failure_page')
            else:
                new_payment = Payment(
                    user=current_user,
                    method=Payment.GIFT,
                    ref_code=0,
                    is_paid=True,
                    price=0,
                    payment_date=timezone.now(),
                    type=Payment.SUBSCRIPTION
                )
                transaction, created = Transaction.objects.get_or_create(
                    user_id=current_user.id,
                    plan_id=plan_id,
                    is_paid=False, defaults={'in_process': False,
                                             'gift_day': plan.plan_gift,
                                             'status': Transaction.SUCCESS_PAYMENT,
                                             'info': "اشتراک هدیه - رایگان",
                                             'try_date': timezone.now()})
                new_payment.save()
                transaction.is_paid = True
                transaction.payment = new_payment
                transaction.save()
                # permission group for subscription
                content_type_audio = ContentType.objects.get_for_model(Audio)
                perm_view_audio, created = Permission.objects.get_or_create(codename=codename_audio_perm(),
                                                                            content_type=content_type_audio)
                content_type_audio_week = ContentType.objects.get_for_model(AudioWeek)
                perm_view_audio_week, created = Permission.objects.get_or_create(
                    codename='can_view_monetary_audio_week',
                    content_type=content_type_audio_week)
                plan_group, plan_group_created = Group.objects.get_or_create(name=group_subscription_name())
                if plan_group_created:
                    plan_group.permissions.add(perm_view_audio, perm_view_audio_week)
                current_user.groups.add(plan_group)

                course_message = " + "
                # guardian permission library
                for course in plan.courses.all():
                    group, created = Group.objects.get_or_create(name=group_course_name(course.title))
                    assign_perm('fully_view_course', group, course)
                    current_user.groups.add(group)
                    course_message += f"دوره {course.name}، "
                messages.success(request, ' اشتراک رایگان با موفقیت به شما اختصاص داده شد. ' + course_message)
                return redirect('success_page')
    messages.error(request, 'متاسفانه در تخصیص اشتراک رایگان به شما خطایی رخ داده است. ')
    return redirect('failure_page')


@login_required
def request_payment(request: HttpRequest, *args, **kwargs):
    current_user: User = request.user
    plan_id = kwargs['plan_id']
    code = kwargs['code']
    current_plan = Plan.objects.filter(id=plan_id, is_active=True).first()
    gift_plan = GiftPlan.objects.filter(code__iexact=code).first()

    # Apply discount if a valid gift code is provided
    if gift_plan:
        current_plan.set_off_price = (gift_plan.percentage, gift_plan.max)

    # Calculate total price
    total_price = current_plan.off_price if current_plan.off_price is not None else current_plan.price
    if total_price < 10000:
        new_payment = Payment.objects.create(
            user=current_user,
            method=Payment.ZARINPAL,
            price=total_price,
            type=Payment.SUBSCRIPTION,
            status=PaymentStatus.INVALID_AMOUNT,  # Set payment status
            error="مبلغ پرداختی نامعتبر است. مبلغ پرداختی باید بیشتر از 10,000 تومان باشد."
            # Store the specific error message
        )
        # messages.error(request, "مبلغ پرداختی باید بیشتر از 10,000 تومان باشد.")
        message_tags = f'failed_payment_contact_us'
        messages.error(request,
                       "مبلغ پرداختی نامعتبر است. مبلغ پرداختی باید بیشتر از 10,000 تومان باشد. لطفا با پشتیبانی تماس بگیرید.",
                       extra_tags=message_tags)
        return redirect('failure_page')

    # Redirect if the price is zero
    if total_price == 0:
        return redirect(reverse('plan_detail'))

    # Check for active subscription and transactions
    if current_user.groups.filter(name=group_subscription_name()).exists():
        if Transaction.objects.filter(user_id=current_user.id, is_paid=True, is_expired=False).exists():
            new_payment = Payment.objects.create(
                user=current_user,
                method=Payment.ZARINPAL,
                price=total_price,
                type=Payment.SUBSCRIPTION,
                status=PaymentStatus.ACTIVE_SUBSCRIPTION,  # Set payment status
                error="شما در حال حاضر دارای یک اشتراک فعال هستید و نیاز به پرداخت مجدد ندارید."
                # Store the specific error message
            )
            tr = Transaction.objects.filter(user_id=current_user.id, is_paid=True, is_expired=False).first()
            if not tr.is_expired_this:
                messages.error(request, "شما در حال حاضر دارای یک اشتراک فعال هستید و نیاز به پرداخت مجدد ندارید.")
                return redirect('failure_page')

    # Check for pending transactions in the last 2 minutes
    limit_minutes_ago = datetime.now() - timedelta(minutes=2)
    if Transaction.objects.filter(
            Q(try_date__gte=limit_minutes_ago) & Q(user=current_user) & Q(in_process=True)).count() > 0:
        new_payment = Payment.objects.create(
            user=current_user,
            method=Payment.ZARINPAL,
            price=total_price,
            type=Payment.SUBSCRIPTION,
            status=PaymentStatus.PENDING_TRANSACTION,  # Set payment status
            error="شما یک عملیات پرداخت در حال انجام دارید."  # Store the specific error message
        )
        message_tags = f'pending_payment'
        messages.error(request, "شما یک عملیات پرداخت در حال انجام دارید. به همین دلیل عملیات ناموفق بود.",
                       extra_tags=message_tags)
        return redirect('failure_page')

    # Mark old transactions as not in process
    for tr in Transaction.objects.filter(user_id=current_user.id, in_process=True):
        tr.in_process = False
        tr.save()

    try:
        with transaction.atomic():  # برای پردازش فقط یک درخواست اتمیک استفاده شده
            # Get or create a new transaction
            current_transaction, created = Transaction.objects.get_or_create(
                user_id=current_user.id,
                plan_id=current_plan.id,
                is_paid=False,
                defaults={'in_process': True, 'gift_day': current_plan.plan_gift}
            )
            if not created:
                current_transaction.in_process = True
                current_transaction.gift_day = current_plan.plan_gift
                current_transaction.try_date = timezone.now()
                current_transaction.save()

            # Create a new payment record
            new_payment = Payment(
                user=current_user,
                method=Payment.ZARINPAL,
                ref_code=0,
                is_paid=False,
                price=total_price,
                type=Payment.SUBSCRIPTION
            )
            new_payment.save()
            current_transaction.payment = new_payment

            # ... (rest of your request_payment code)
            callback_url = request.build_absolute_uri(reverse('verify_payment'))

            data = {
                "MerchantID": MERCHANT,
                "Amount": total_price,  # Amount in Toman
                "Description": description,
                "Phone": current_user.mobile,
                "CallbackURL": callback_url,
            }

            headers = {'content-type': 'application/json', 'content-length': str(len(json.dumps(data)))}

            try:
                # Send request to ZarinPal
                response = requests.post(ZP_API_REQUEST, data=json.dumps(data), headers=headers, timeout=10)

                if response.status_code == 200:
                    response_json = response.json()
                    if response_json['Status'] == 100:
                        authority = response_json['Authority']
                        new_payment.status = PaymentStatus.PENDING_NO_ERRORS
                        new_payment.save()
                        current_transaction.status = Transaction.STATUS_CODES["BEFORE_PAYMENT"]
                        current_transaction.info = 'No errors - NOT PAID'
                        current_transaction.save()
                        return redirect(ZP_API_STARTPAY + authority)  # Redirect to ZarinPal payment gateway
                    else:
                        error_code = response_json['Status']
                        error_message = get_zarinpal_error_message(error_code)  # Get error message
                        new_payment.error = f"خطا در پرداخت زرین پال: {error_message} (کد: {error_code})"
                        new_payment.save()
                        current_transaction.status = Transaction.STATUS_CODES["ERROR_BEFORE_PAYMENT"]
                        current_transaction.info = f"Zarinpal Error code: {error_code}"
                        current_transaction.save()
                        return HttpResponse(f"Zarinpal Error code: {error_code}")
                else:
                    new_payment.status = PaymentStatus.REQUEST_ERROR  # Set payment status
                    new_payment.error = f"Request failed with status code: {response.status_code}"  # Store the specific error message
                    new_payment.save()
                    current_transaction.status = Transaction.STATUS_CODES["ERROR_BEFORE_PAYMENT"]
                    current_transaction.info = f"Request failed with status code: {response.status_code}"
                    current_transaction.save()
                    return HttpResponse(f"Request failed with status code: {response.status_code}")

            except requests.exceptions.Timeout:
                new_payment.status = PaymentStatus.TIMEOUT_ERROR  # Set payment status
                new_payment.error = "Request timed out."  # Store the specific error message
                new_payment.save()
                current_transaction.status = Transaction.STATUS_CODES["ERROR_BEFORE_PAYMENT"]
                current_transaction.info = "Request timed out."
                current_transaction.save()
                return HttpResponse("Request timed out.")
            except requests.exceptions.ConnectionError:
                new_payment.status = PaymentStatus.CONNECTION_ERROR  # Set payment status
                new_payment.error = "Connection error."  # Store the specific error message
                new_payment.save()
                current_transaction.status = Transaction.STATUS_CODES["ERROR_BEFORE_PAYMENT"]
                current_transaction.info = "Connection error."
                current_transaction.save()
                return HttpResponse("Connection error.")
            except Exception as e:
                new_payment.status = PaymentStatus.UNKNOWN_ERROR  # Set payment status
                new_payment.error = f"An unexpected error occurred: {e}"  # Store the specific error message
                new_payment.save()
                current_transaction.status = Transaction.STATUS_CODES["ERROR_BEFORE_PAYMENT"]
                current_transaction.info = f"An unexpected error occurred: {e}"
                current_transaction.save()
                return HttpResponse(f"An unexpected error occurred: {e}")

    except OperationalError as e:
        if "could not obtain lock" in str(e):
            new_payment = Payment.objects.create(
                user=current_user,
                method=Payment.ZARINPAL,
                price=total_price,
                type=Payment.SUBSCRIPTION,
                status=PaymentStatus.LOCKING_ERROR,  # Set payment status
                error="شما یک عملیات پرداخت در حال انجام دارید. لطفا چند لحظه دیگر تلاش کنید."
                # Store the specific error message
            )
            message_tags = f'pending_payment'
            messages.error(request, "شما یک عملیات پرداخت در حال انجام دارید. لطفا چند لحظه دیگر تلاش کنید.",
                           extra_tags=message_tags)
            return redirect('failure_page')
        elif "database is locked" in str(e):
            new_payment = Payment.objects.create(
                user=current_user,
                method=Payment.ZARINPAL,
                price=total_price,
                type=Payment.SUBSCRIPTION,
                status=PaymentStatus.LOCKING_ERROR,  # Set payment status
                error="شما یک عملیات پرداخت در حال انجام دارید. لطفا چند لحظه دیگر تلاش کنید."
                # Store the specific error message
            )
            message_tags = f'failed_payment'
            messages.error(request, "در حال حاضر امکان پرداخت وجود ندارد. لطفا بعدا تلاش کنید.",
                           extra_tags=message_tags)
            return redirect('failure_page')
        else:
            # Handle other OperationalErrors
            return HttpResponse(f"A database error occurred: {e}")

@login_required
def verify_payment(request: HttpRequest):
    current_user: User = request.user

    t_authority = request.GET.get('Authority')
    t_status = request.GET.get('Status')

    try:
        with transaction.atomic():  # Lock transaction for processing
            current_transaction = Transaction.objects.select_for_update().filter(
                user_id=current_user.id, in_process=True).first()

            if not current_transaction:
                return HttpResponse("تراکنش یافت نشد.")

            current_payment = Payment.objects.filter(id=current_transaction.payment_id).first()
            current_plan = Plan.objects.filter(id=current_transaction.plan_id).first()
            total_price = current_plan.price

            if t_status == 'OK':
                req_header = {"accept": "application/json", "content-type": "application/json"}
                req_data = {
                    "MerchantID": MERCHANT,
                    "Amount": total_price,
                    "Authority": t_authority
                }
                try:
                    req = requests.post(ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header,
                                        timeout=10)  # Timeout added
                    response_data = req.json()

                    if req.status_code == 200:
                        if response_data['Status'] == 100:
                            ref_str = response_data['RefID']
                            current_time = timezone.now()

                            current_payment.is_paid = True
                            current_payment.payment_date = current_time
                            current_payment.ref_code = ref_str
                            current_payment.status = PaymentStatus.PAID_NO_ERRORS
                            current_payment.save()

                            current_transaction.in_process = False
                            current_transaction.is_paid = True
                            current_transaction.start_date = current_time
                            current_transaction.calculate_expire_date()
                            current_transaction.status = Transaction.STATUS_CODES["SUCCESS_PAYMENT"]
                            current_transaction.info = f"پرداخت موفق توسط refId = {ref_str} کاربر: {current_user.username}"
                            current_transaction.save()

                            # Assign permissions for subscription
                            content_type_audio = ContentType.objects.get_for_model(Audio)
                            perm_view_audio, created = Permission.objects.get_or_create(codename=codename_audio_perm(),
                                                                                        content_type=content_type_audio)
                            content_type_audio_week = ContentType.objects.get_for_model(AudioWeek)
                            perm_view_audio_week, created = Permission.objects.get_or_create(
                                codename='can_view_monetary_audio_week',
                                content_type=content_type_audio_week)
                            plan_group, plan_group_created = Group.objects.get_or_create(name=group_subscription_name())
                            if plan_group_created:
                                plan_group.permissions.add(perm_view_audio, perm_view_audio_week)
                            current_user.groups.add(plan_group)

                            # Grant course access
                            for course in current_plan.courses.all():
                                group, created = Group.objects.get_or_create(name=group_course_name(course.title))
                                assign_perm('fully_view_course', group, course)
                                current_user.groups.add(group)

                            send_new_subscription_sms(current_user.mobile, current_transaction.plan.name,
                                                      current_transaction.plan.duration,
                                                      current_transaction.end_date)

                            return render(request, 'payment_detail.html', {
                                'transaction': current_transaction,
                                'success': f'تراکنش شما با کد پیگیری {ref_str} با موفقیت انجام شد',
                            })

                        elif response_data['Status'] == 101:
                            current_payment.status = PaymentStatus.DUPLICATE_TRANSACTION
                            current_payment.error = "این تراکنش قبلا ثبت شده است"
                            current_payment.save()

                            current_transaction.in_process = False
                            current_transaction.save()

                            return render(request, 'payment_detail.html', {
                                'transaction': current_transaction,
                                'info': 'این تراکنش قبلا ثبت شده است'
                            })

                        else:
                            error_code = response_data['Status']
                            error_message = get_zarinpal_error_message(error_code)
                            current_payment.status = PaymentStatus.ZARINPAL_ERROR
                            current_payment.error = f"خطا در پرداخت زرین پال: {error_message} (کد: {error_code})"
                            current_payment.save()

                            current_transaction.in_process = False
                            current_transaction.save()

                            return render(request, 'payment_detail.html', {
                                'transaction': current_transaction,
                                'error': f"خطا در پرداخت زرین پال: {error_message} (کد: {error_code})"
                            })
                    else:
                        e_code = response_data.get('errors', {}).get('code', 'unknown')
                        e_message = response_data.get('errors', {}).get('message', 'Unknown error')
                        current_payment.status = PaymentStatus.REQUEST_ERROR
                        current_payment.error = f"خطا در درخواست به زرین پال: کد {e_code} - پیام: {e_message}"
                        current_payment.save()

                        current_transaction.in_process = False
                        current_transaction.save()

                        return render(request, 'payment_detail.html', {
                            'transaction': current_transaction,
                            'error': f"خطا در درخواست به زرین پال: کد {e_code} - پیام: {e_message}"
                        })
                except requests.exceptions.Timeout:
                    current_payment.status = PaymentStatus.TIMEOUT_ERROR
                    current_payment.error = "درخواست به زرین پال timeout شد."
                    current_payment.save()

                    current_transaction.in_process = False
                    current_transaction.save()

                    return render(request, 'payment_detail.html', {
                        'transaction': current_transaction,
                        'error': "درخواست به زرین پال timeout شد."
                    })

                except requests.exceptions.ConnectionError:
                    current_payment.status = PaymentStatus.CONNECTION_ERROR
                    current_payment.error = "خطا در اتصال به زرین پال."
                    current_payment.save()

                    current_transaction.in_process = False
                    current_transaction.save()

                    return render(request, 'payment_detail.html', {
                        'transaction': current_transaction,
                        'error': "خطا در اتصال به زرین پال."
                    })
                except Exception as e:
                    current_payment.status = PaymentStatus.UNKNOWN_ERROR
                    current_payment.error = f"یک خطای غیرمنتظره در درخواست به زرین پال رخ داد: {e}"
                    current_payment.save()

                    current_transaction.in_process = False
                    current_transaction.save()

                    return render(request, 'payment_detail.html', {
                        'transaction': current_transaction,
                        'error': f"یک خطای غیرمنتظره رخ داد: {e}"
                    })

            else:  # Status is not OK (e.g., user cancelled)
                current_payment.status = PaymentStatus.USER_CANCELLED
                current_payment.error = 'پرداخت توسط کاربر لغو شد.'
                current_payment.save()

                current_transaction.in_process = False
                current_transaction.save()

                return render(request, 'payment_detail.html', {
                    'transaction': current_transaction,
                    'error': 'پرداخت توسط کاربر لغو شد.'
                })

    except OperationalError as e:
        current_payment.status = PaymentStatus.DATABASE_ERROR
        current_payment.error = f"خطای پایگاه داده: {e}"
        current_payment.save()
        return HttpResponse(f"خطای پایگاه داده: {e}")

    except Exception as e:
        current_payment.status = PaymentStatus.UNKNOWN_ERROR
        current_payment.error = f"یک خطای غیرمنتظره رخ داد: {e}"
        current_payment.save()
        return HttpResponse(f"یک خطای غیرمنتظره رخ داد: {e}")



@login_required
def request_campaign_payment(request: HttpRequest, *args, **kwargs):
    current_user: User = request.user
    campaign_id = kwargs['campaign_id']
    category_id = kwargs['category_id']  # دریافت category_id از kwargs
    code = kwargs.get('code', None)  # دریافت کد هدیه در صورت وجود
    current_campaign = Campaign.objects.filter(id=campaign_id, is_open=True).first()
    gift_campaign = GiftPlan.objects.filter(code__iexact=code).first() if code else None

    # Apply discount if a valid gift code is provided
    if gift_campaign:
        current_campaign.set_off_price = (gift_campaign.percentage, gift_campaign.max)

    # Calculate total price
    total_price = current_campaign.off_price if current_campaign.off_price is not None else current_campaign.price
    if total_price < 10000:
        new_payment = Payment.objects.create(
            user=current_user,
            method=Payment.ZARINPAL,
            price=total_price,
            type=Payment.CAMPAIGN,
            status=PaymentStatus.INVALID_AMOUNT,
            error="مبلغ پرداختی نامعتبر است. مبلغ پرداختی باید بیشتر از 10,000 تومان باشد."
        )
        message_tags = f'failed_payment_contact_us'
        messages.error(request,
                       "مبلغ پرداختی نامعتبر است. مبلغ پرداختی باید بیشتر از 10,000 تومان باشد. لطفا با پشتیبانی تماس بگیرید.",
                       extra_tags=message_tags)
        return redirect('failure_page')

    # Redirect if the price is zero
    if total_price == 0:
        return redirect(reverse('campaign_detail', kwargs={'campaign_id': campaign_id}))

    # Check for active campaign transactions
    if CTransaction.objects.filter(user_id=current_user.id, is_paid=True, is_expired=False,
                                   campaign__is_active=True,
                                   campaign_id=campaign_id, category_id=category_id).exists():

        tr = CTransaction.objects.filter(user_id=current_user.id, is_paid=True, is_expired=False,
                                         campaign__is_active=True,
                                         campaign_id=campaign_id, category_id=category_id).first()
        if tr.is_expired_this:
            try:
                remove_perm('fully_view_campaign', current_user, current_campaign)
                # سایر عملیات مربوط به انقضای اشتراک
            except Campaign.DoesNotExist:
                # مدیریت خطای عدم وجود Campaign
                pass
            has_campaign = False
        else:
            new_payment = Payment.objects.create(
                user=current_user,
                method=Payment.ZARINPAL,
                price=total_price,
                type=Payment.CAMPAIGN,
                status=PaymentStatus.ACTIVE_SUBSCRIPTION,
                error="شما در حال حاضر دارای یک کمپین فعال هستید و نیاز به پرداخت مجدد ندارید."
            )
            messages.error(request, "شما در حال حاضر دارای یک کمپین فعال هستید و نیاز به پرداخت مجدد ندارید.")
            return redirect('failure_page')

    # Check for pending transactions in the last 2 minutes
    limit_minutes_ago = datetime.now() - timedelta(minutes=2)
    if CTransaction.objects.filter(
            Q(try_date__gte=limit_minutes_ago) & Q(user=current_user) & Q(in_process=True) & Q(campaign_id=campaign_id) & Q(category_id=category_id)).count() > 0:
        new_payment = Payment.objects.create(
            user=current_user,
            method=Payment.ZARINPAL,
            price=total_price,
            type=Payment.CAMPAIGN,
            status=PaymentStatus.PENDING_TRANSACTION,
            error="شما یک عملیات پرداخت در حال انجام دارید."
        )
        message_tags = f'pending_payment'
        messages.error(request, "شما یک عملیات پرداخت در حال انجام دارید. به همین دلیل عملیات ناموفق بود.",
                       extra_tags=message_tags)
        return redirect('failure_page')

    # Mark old transactions as not in process
    for tr in CTransaction.objects.filter(user_id=current_user.id, in_process=True, campaign_id=campaign_id, category_id=category_id):
        tr.in_process = False
        tr.save()

    try:
        with transaction.atomic():
            # Get or create a new Campaign transaction
            current_c_transaction, created = CTransaction.objects.get_or_create(
                user_id=current_user.id,
                campaign_id=current_campaign.id,
                category_id=category_id,
                is_paid=False,
                defaults={'in_process': True, 'gift_day': current_campaign.campaign_gift}
            )
            if not created:
                current_c_transaction.in_process = True
                current_c_transaction.gift_day = current_campaign.campaign_gift
                current_c_transaction.try_date = timezone.now()
                current_c_transaction.save()

            # Get or create a new global Transaction
            current_transaction, created = Transaction.objects.get_or_create(
                user_id=current_user.id,
                plan=None,
                is_paid=False,
                defaults={'in_process': True}
            )
            if not created:
                current_transaction.in_process = True
                current_transaction.try_date = timezone.now()
                current_transaction.save()

            # Create a new payment record
            new_payment = Payment(
                user=current_user,
                method=Payment.ZARINPAL,
                ref_code=0,
                is_paid=False,
                price=total_price,
                type=Payment.CAMPAIGN
            )
            new_payment.save()
            current_c_transaction.payment = new_payment
            current_transaction.payment = new_payment

            callback_url = request.build_absolute_uri(reverse('verify_campaign_payment'))

            data = {
                "MerchantID": MERCHANT,
                "Amount": total_price,
                "Description": description,
                "Phone": current_user.mobile,
                "CallbackURL": callback_url,
            }

            headers = {'content-type': 'application/json', 'content-length': str(len(json.dumps(data)))}
            try:
                response = requests.post(ZP_API_REQUEST, data=json.dumps(data), headers=headers, timeout=10)

                if response.status_code == 200:
                    response_json = response.json()
                    if response_json['Status'] == 100:
                        authority = response_json['Authority']
                        new_payment.status = PaymentStatus.PENDING_NO_ERRORS
                        new_payment.save()
                        current_c_transaction.status = CTransaction.STATUS_CODES["BEFORE_PAYMENT"]
                        current_c_transaction.info = 'No errors - NOT PAID'
                        current_c_transaction.save()
                        current_transaction.status = Transaction.STATUS_CODES["BEFORE_PAYMENT"]
                        current_transaction.info = 'No errors - NOT PAID'
                        current_transaction.save()

                        # بررسی Transaction منقضی نشده
                        if current_user.groups.filter(name=group_subscription_name()).exists():
                            old_transaction = Transaction.objects.filter(user=current_user, is_paid=True,
                                                                         is_expired=False).first()
                            if not old_transaction.is_expired_this:
                                # محاسبه زمان باقیمانده از Transaction قبلی
                                remaining_time = old_transaction.end_date - timezone.now()
                                remaining_days = remaining_time.days

                                # حذف Transaction قبلی
                                old_transaction.is_expired = True

                                # محاسبه end_date برای Transaction جدید
                                current_transaction.start_date = timezone.now()
                                current_transaction.end_date = current_transaction.start_date.date() + timedelta(
                                    days=current_campaign.duration + remaining_days)
                                current_transaction.save()

                        else:
                            # محاسبه end_date برای Transaction جدید بر اساس duration کمپین
                            current_transaction.start_date = timezone.now()
                            current_transaction.end_date = current_transaction.start_date.date() + timedelta(
                                days=current_campaign.duration)
                            current_transaction.save()

                        return redirect(ZP_API_STARTPAY + authority)
                    else:
                        error_code = response_json['Status']
                        error_message = get_zarinpal_error_message(error_code)
                        new_payment.error = f"خطا در پرداخت زرین پال: {error_message} (کد: {error_code})"
                        new_payment.save()
                        current_c_transaction.status = CTransaction.STATUS_CODES["ERROR_BEFORE_PAYMENT"]
                        current_c_transaction.info = f"Zarinpal Error code: {error_code}"
                        current_c_transaction.save()
                        current_transaction.status = Transaction.STATUS_CODES["ERROR_BEFORE_PAYMENT"]
                        current_transaction.info = f"Zarinpal Error code: {error_code}"
                        current_transaction.save()
                        return HttpResponse(f"Zarinpal Error code: {error_code}")
                else:
                    new_payment.status = PaymentStatus.REQUEST_ERROR
                    new_payment.error = f"Request failed with status code: {response.status_code}"
                    new_payment.save()
                    current_c_transaction.status = CTransaction.STATUS_CODES["ERROR_BEFORE_PAYMENT"]
                    current_c_transaction.info = f"Request failed with status code: {response.status_code}"
                    current_c_transaction.save()
                    current_transaction.status = Transaction.STATUS_CODES["ERROR_BEFORE_PAYMENT"]
                    current_transaction.info = f"Request failed with status code: {response.status_code}"
                    current_transaction.save()
                    return HttpResponse(f"Request failed with status code: {response.status_code}")

            except requests.exceptions.Timeout:
                new_payment.status = PaymentStatus.TIMEOUT_ERROR
                new_payment.error = "Request timed out."
                new_payment.save()
                current_c_transaction.status = CTransaction.STATUS_CODES["ERROR_BEFORE_PAYMENT"]
                current_c_transaction.info = "Request timed out."
                current_c_transaction.save()
                current_transaction.status = Transaction.STATUS_CODES["ERROR_BEFORE_PAYMENT"]
                current_transaction.info = "Request timed out."
                current_transaction.save()
                return HttpResponse("Request timed out.")
            except requests.exceptions.ConnectionError:
                new_payment.status = PaymentStatus.CONNECTION_ERROR
                new_payment.error = "Connection error."
                new_payment.save()
                current_c_transaction.status = CTransaction.STATUS_CODES["ERROR_BEFORE_PAYMENT"]
                current_c_transaction.info = "Connection error."
                current_c_transaction.save()
                current_transaction.status = Transaction.STATUS_CODES["ERROR_BEFORE_PAYMENT"]
                current_transaction.info = "Connection error."
                current_transaction.save()
                return HttpResponse("Connection error.")
    except Exception as e:
        new_payment.status = PaymentStatus.UNKNOWN_ERROR
        new_payment.error = f"An unexpected error occurred: {e}"
        new_payment.save()
        current_c_transaction.status = CTransaction.STATUS_CODES["ERROR_BEFORE_PAYMENT"]
        current_c_transaction.info = f"An unexpected error occurred: {e}"
        current_c_transaction.save()
        current_transaction.status = Transaction.STATUS_CODES["ERROR_BEFORE_PAYMENT"]
        current_transaction.info = f"An unexpected error occurred: {e}"
        current_transaction.save()
        return HttpResponse(f"An unexpected error occurred: {e}")

@login_required
def verify_campaign_payment(request: HttpRequest):
    current_user: User = request.user

    t_authority = request.GET.get('Authority')
    t_status = request.GET.get('Status')

    try:
        with transaction.atomic():  # Lock transaction for processing
            current_c_transaction = CTransaction.objects.select_for_update().filter(
                user_id=current_user.id, in_process=True).first()
            if not current_c_transaction:
                return HttpResponse("تراکنش یافت نشد.")

            current_transaction = Transaction.objects.select_for_update().filter(
                user_id=current_user.id, in_process=True, payment_id=current_c_transaction.payment_id).first()
            if not current_transaction:
                return HttpResponse("تراکنش اصلی یافت نشد.")

            current_payment = Payment.objects.filter(id=current_c_transaction.payment_id).first()
            current_campaign = Campaign.objects.filter(id=current_c_transaction.campaign_id).first()
            total_price = current_campaign.price

            if t_status == 'OK':
                req_header = {"accept": "application/json", "content-type": "application/json"}
                req_data = {
                    "MerchantID": MERCHANT,
                    "Amount": total_price,
                    "Authority": t_authority
                }
                try:
                    req = requests.post(ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header,
                                        timeout=10)  # Timeout added
                    response_data = req.json()

                    if req.status_code == 200:
                        if response_data['Status'] == 100:
                            ref_str = response_data['RefID']
                            current_time = timezone.now()

                            current_payment.is_paid = True
                            current_payment.payment_date = current_time
                            current_payment.ref_code = ref_str
                            current_payment.status = PaymentStatus.PAID_NO_ERRORS
                            current_payment.save()

                            current_c_transaction.in_process = False
                            current_c_transaction.is_paid = True
                            current_c_transaction.start_date = current_time
                            current_c_transaction.calculate_expire_date()
                            current_c_transaction.status = CTransaction.STATUS_CODES["SUCCESS_PAYMENT"]
                            current_c_transaction.info = f"پرداخت موفق توسط refId = {ref_str} کاربر: {current_user.username}"
                            current_c_transaction.save()

                            current_transaction.in_process = False
                            current_transaction.is_paid = True
                            current_transaction.start_date = current_time

                            # بررسی Transaction منقضی نشده
                            old_transaction = Transaction.objects.filter(user=current_user, is_expired=False).first()
                            if old_transaction:
                                remaining_days = old_transaction.left_days()
                                current_transaction.end_date = current_time.date() + timedelta(
                                    days=current_campaign.duration + remaining_days)
                                old_transaction.is_expired = True
                                old_transaction.save()
                            else:
                                current_transaction.end_date = current_time.date() + timedelta(
                                    days=current_campaign.duration)

                            current_transaction.status = Transaction.STATUS_CODES["SUCCESS_PAYMENT"]
                            current_transaction.info = f"پرداخت موفق توسط refId = {ref_str} کاربر: {current_user.username}"
                            current_transaction.save()

                            # Assign permissions for subscription
                            content_type_audio = ContentType.objects.get_for_model(Audio)
                            perm_view_audio, created = Permission.objects.get_or_create(codename=codename_audio_perm(),
                                                                                        content_type=content_type_audio)
                            content_type_audio_week = ContentType.objects.get_for_model(AudioWeek)
                            perm_view_audio_week, created = Permission.objects.get_or_create(
                                codename='can_view_monetary_audio_week',
                                content_type=content_type_audio_week)
                            plan_group, plan_group_created = Group.objects.get_or_create(name=group_subscription_name())
                            if plan_group_created:
                                plan_group.permissions.add(perm_view_audio, perm_view_audio_week)
                            current_user.groups.add(plan_group)

                            # Grant campaign access using django-guardian
                            assign_perm('fully_view_campaign', current_user, current_campaign)

                            # Grant course access
                            courses = current_campaign.courses.all()
                            for course in courses:
                                group, created = Group.objects.get_or_create(name=group_course_name(course.title))
                                assign_perm('fully_view_course', group, course)
                                current_user.groups.add(group)

                            send_new_campaign_sms(current_user.mobile, current_c_transaction.campaign.name,
                                                      current_c_transaction.campaign.duration,
                                                      current_c_transaction.end_date)


                            return render(request, 'payment_detail.html', {
                                'c_transaction': current_c_transaction,
                                'transaction': current_transaction,
                                'success': f'تراکنش شما با کد پیگیری {ref_str} با موفقیت انجام شد',
                            })

                        elif response_data['Status'] == 101:
                            current_payment.status = PaymentStatus.DUPLICATE_TRANSACTION
                            current_payment.error = "این تراکنش قبلا ثبت شده است"
                            current_payment.save()

                            current_transaction.in_process = False
                            current_transaction.save()

                            return render(request, 'payment_detail.html', {
                                'transaction': current_transaction,
                                'info': 'این تراکنش قبلا ثبت شده است'
                            })

                        else:
                            error_code = response_data['Status']
                            error_message = get_zarinpal_error_message(error_code)
                            current_payment.status = PaymentStatus.ZARINPAL_ERROR
                            current_payment.error = f"خطا در پرداخت زرین پال: {error_message} (کد: {error_code})"
                            current_payment.save()

                            current_transaction.in_process = False
                            current_transaction.save()

                            return render(request, 'payment_detail.html', {
                                'transaction': current_transaction,
                                'error': f"خطا در پرداخت زرین پال: {error_message} (کد: {error_code})"
                            })
                    else:
                        e_code = response_data.get('errors', {}).get('code', 'unknown')
                        e_message = response_data.get('errors', {}).get('message', 'Unknown error')
                        current_payment.status = PaymentStatus.REQUEST_ERROR
                        current_payment.error = f"خطا در درخواست به زرین پال: کد {e_code} - پیام: {e_message}"
                        current_payment.save()

                        current_transaction.in_process = False
                        current_transaction.save()

                        return render(request, 'payment_detail.html', {
                            'transaction': current_transaction,
                            'error': f"خطا در درخواست به زرین پال: کد {e_code} - پیام: {e_message}"
                        })
                except requests.exceptions.Timeout:
                    current_payment.status = PaymentStatus.TIMEOUT_ERROR
                    current_payment.error = "درخواست به زرین پال timeout شد."
                    current_payment.save()

                    current_transaction.in_process = False
                    current_transaction.save()

                    return render(request, 'payment_detail.html', {
                        'transaction': current_transaction,
                        'error': "درخواست به زرین پال timeout شد."
                    })

                except requests.exceptions.ConnectionError:
                    current_payment.status = PaymentStatus.CONNECTION_ERROR
                    current_payment.error = "خطا در اتصال به زرین پال."
                    current_payment.save()

                    current_transaction.in_process = False
                    current_transaction.save()

                    return render(request, 'payment_detail.html', {
                        'transaction': current_transaction,
                        'error': "خطا در اتصال به زرین پال."
                    })
                except Exception as e:
                    current_payment.status = PaymentStatus.UNKNOWN_ERROR
                    current_payment.error = f"یک خطای غیرمنتظره در درخواست به زرین پال رخ داد: {e}"
                    current_payment.save()

                    current_transaction.in_process = False
                    current_transaction.save()

                    return render(request, 'payment_detail.html', {
                        'transaction': current_transaction,
                        'error': f"یک خطای غیرمنتظره رخ داد: {e}"
                    })

            else:  # Status is not OK (e.g., user cancelled)
                current_payment.status = PaymentStatus.USER_CANCELLED
                current_payment.error = 'پرداخت توسط کاربر لغو شد.'
                current_payment.save()

                current_transaction.in_process = False
                current_transaction.save()

                return render(request, 'payment_detail.html', {
                    'transaction': current_transaction,
                    'error': 'پرداخت توسط کاربر لغو شد.'
                })

    except OperationalError as e:
        current_payment.status = PaymentStatus.DATABASE_ERROR
        current_payment.error = f"خطای پایگاه داده: {e}"
        current_payment.save()
        return HttpResponse(f"خطای پایگاه داده: {e}")

    except Exception as e:
        current_payment.status = PaymentStatus.UNKNOWN_ERROR
        current_payment.error = f"یک خطای غیرمنتظره رخ داد: {e}"
        current_payment.save()
        return HttpResponse(f"یک خطای غیرمنتظره رخ داد: {e}")

def get_zarinpal_error_message(error_code):
    error_messages = {
        "-1": "اطلاعات ارسال شده ناقص است.",
        "-2": "IP و یا مرچنت کد پذیرنده صحیح نیست.",
        "-3": "با توجه به محدودیت‌های شاپرک امکان پرداخت با رقم درخواست شده میسر نمی‌باشد.",
        "-4": "سطح تایید پذیرنده پایین‌تر از سطح نقره‌ای است.",
        "-11": "درخواست مورد نظر یافت نشد.",
        "-12": "امکان ویرایش درخواست میسر نمی‌باشد.",
        "-21": "هیچ نوع عملیات مالی برای این تراکنش یافت نشد.",
        "-22": "تراکنش ناموفق می‌باشد.",
        "-33": "رقم تراکنش با رقم پرداخت شده مطابقت ندارد.",
        "-34": "سقف تقسیم تراکنش از لحاظ تعداد یا رقم عبور نموده است.",
        "-40": "اجازه دسترسی به متد مربوطه وجود ندارد.",
        "-41": "اطلاعات ارسال شده مربوط به AdditionalData غیرمعتبر می‌باشد.",
        "-42": "مدت زمان معتبر طول عمر شناسه پرداخت باید بین 30 دقیقه تا 45 روز می‌باشد.",
        "-54": "درخواست مورد نظر آرشیو شده است.",
        "100": "عملیات با موفقیت انجام گردیده است.",
        "101": "عملیات پرداخت موفق بوده و قبلا PaymentVerification تراکنش انجام شده است."
    }
    return error_messages.get(str(error_code), "خطای نامشخص از زرین پال")  # Default message


#  ----------------------- start admin views --------------------------------

@login_required
def try_pay_sms(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    user = payment.user  # Get the user associated with the payment

    if request.method == 'POST':
        if user.is_active:  # Check if the user is active FIRST
            if send_try_pay_sms(user.mobile, user.username, payment.create_date):  # Add timeout
                payment.error = payment.error or ""  # Check if None and initialize to empty string
                payment.error += " - sms_sent"  # Append to the existing error message
                payment.save()
                messages.success(request, 'پیامک با موفقیت ارسال شد.')
            else:
                payment.error = payment.error or ""  # Check if None and initialize to empty string
                payment.error += " - sms_failed"  # Append to the existing error message
                payment.save()
                messages.error(request, 'ارسال پیامک ناموفق بود.')
        else:
            messages.info(request, 'کاربر هنوز فعال نشده است.')  # Inform the user if not active

        return redirect('admin:ks_subscription_payment_changelist')  # Redirect to payment list

    context = {'user': user, 'payment': payment, 'title': 'ارسال پیامک'}
    return render(request, 'admin/auth/payment/try_pay_sms.html', context)

#  ===================== end admin views =====================================
