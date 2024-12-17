from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from guardian.shortcuts import assign_perm

from ks_account.models import User
from ks_audio.models import Audio, AudioWeek
from ks_site.models import SiteSetting
from ks_subscription.models import Plan, Payment, Transaction
import time
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.urls import reverse
from django.shortcuts import redirect, render
import requests
import json

from utility.choices import PaymentStatus
from utility.utils import group_subscription_name, codename_audio_week_perm, codename_audio_perm, group_course_name

# Create your views here.


MERCHANT = '646f0c9b-d41f-464d-a7d4-7e83ccd6e719'
ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"
amount = 0  # Rial / Required
description = "نهایی کردن خرید اشتراک خیلی ساده ست"  # Required
email = ''  # Optional
mobile = ''  # Optional
# Important: need to edit for realy server.
CallbackURL = 'http://127.0.0.1:8000/subscription/verify-payment/'


class PlansList(ListView):
    template_name = 'plans.html'
    paginate_by = 3

    # context_object_name = 'plans'

    def get_queryset(self):
        return Plan.objects.filter(is_active=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PlansList, self).get_context_data()
        setting: SiteSetting = SiteSetting.objects.filter(is_main_setting=True).first()
        context['site_setting'] = setting
        return context


@method_decorator(login_required, name='dispatch')
class PlanDetailView(DetailView):
    model = Plan
    template_name = 'plan_detail.html'
    paginate_by = 3

    def get_queryset(self):
        query = super(PlanDetailView, self).get_queryset()
        query = query.filter(is_active=True)
        return query

    def get_context_data(self, **kwargs):
        context = super(PlanDetailView, self).get_context_data()
        plan: Plan = kwargs.get('object')

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

        return context


@login_required
def request_payment(request: HttpRequest, *args, **kwargs):
    current_user: User = request.user
    plan_id = kwargs['plan_id']
    current_plan: Plan = Plan.objects.filter(id=plan_id, is_active=True).first()
    total_price = current_plan.price
    if total_price == 0:
        return redirect(reverse('plan_detail'))

    # permission group for subscription
    has_perm = current_user.groups.filter(name=group_subscription_name()).exists()

    # agar useri transaction active va expire nashode darad natavanad pardakht konad
    for transaction in Transaction.objects.filter(user_id=current_user.id, is_paid=True):
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
        else:
            messages.error(request,
                           "شما در حال حاضر یک اشتراک فعال دارید و نیاز به تهیه اشتراک جدید ندارید.")
            return redirect('failure_page')

    # agar useri dar 10 min ghabl in_process darad ke natavanad pardakht konad
    # agar Na in_process ha hame False shavad va betavanad pardakht konad
    limit_minutes_ago = datetime.now() - timedelta(minutes=10)
    count_transaction_in_process_in_last_limit_min = Transaction.objects.filter(
        Q(try_date__gte=limit_minutes_ago) & Q(user=current_user) & Q(in_process=True)).count()
    if count_transaction_in_process_in_last_limit_min > 0:
        messages.error(request,
                       "شما در حال حاضر یک عملیات پرداخت ناتمام دارید. لطفا عملیات قبلی را پرداخت یا لغو کنید.")
        return redirect('failure_page')

    for transaction in Transaction.objects.filter(user_id=current_user.id, in_process=True):
        transaction.in_process = False
        transaction.save()
    current_transaction, created = Transaction.objects.get_or_create(user_id=current_user.id, plan_id=plan_id,
                                                                     is_paid=False, defaults={
            'in_process': True,
            'gift_day': current_plan.plan_gift})
    if not created:
        current_transaction.try_date = timezone.now()
        current_transaction.save()

    new_payment = Payment(
        user=current_user,
        method=Payment.ZARINPAL,
        ref_code=0,
        is_paid=False,
        price=total_price,
        type=Payment.SUBSCRIPTION
    )
    req_data = {
        "merchant_id": MERCHANT,
        "amount": total_price * 10,
        "callback_url": CallbackURL,
        "description": description,
        "metadata": {"mobile": current_user.mobile, "email": email}
    }
    req_header = {"accept": "application/json", "content-type": "application/json'"}
    req = requests.post(url=ZP_API_REQUEST, data=json.dumps(req_data), headers=req_header)
    authority = req.json()['data']['authority']
    if len(req.json()['errors']) == 0:
        new_payment.status = PaymentStatus.PENDING_NO_ERRORS
        new_payment.save()
        current_transaction.payment = new_payment
        current_transaction.status = Transaction.BEFORE_PAYMENT
        current_transaction.info = 'No errors - NOT PAID'
        current_transaction.save()
        return redirect(ZP_API_STARTPAY.format(authority=authority))
    else:
        e_code = req.json()['errors']['code']
        e_message = req.json()['errors']['message']
        new_payment.status = PaymentStatus.error(e_code)
        new_payment.save()
        current_transaction.status = Transaction.ERROR_BEFORE_PAYMENT,
        current_transaction.info = f"Error code: {e_code}, Error Message: {e_message}"
        current_transaction.save()
        return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")


@login_required
def verify_payment(request: HttpRequest):
    test = True
    current_user: User = request.user
    current_transaction: Transaction = Transaction.objects.filter(user_id=current_user.id, in_process=True).first()
    current_payment: Payment = Payment.objects.filter(id=current_transaction.payment_id).first()
    current_plan = Plan.objects.filter(id=current_transaction.plan_id).first()
    total_price = current_plan.price

    t_authority = request.GET['Authority']
    if request.GET.get('Status') == 'OK':
        req_header = {"accept": "application/json", "content-type": "application/json'"}
        req_data = {
            "merchant_id": MERCHANT,
            "amount": total_price * 10,
            "authority": t_authority
        }
        req = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
        if len(req.json()['errors']) == 0:
            t_status = req.json()['data']['code']

            if t_status == 100:
                ref_str = req.json()['data']['ref_id']
                current_payment.is_paid = True
                current_payment.payment_date = time.time()
                current_payment.ref_code = req.json()['data']['ref_id']
                current_payment.status = PaymentStatus.PAID_NO_ERRORS
                current_payment.save()
                current_transaction.in_process = False
                current_transaction.is_paid = True
                current_transaction.start_date = datetime.now()
                current_transaction.calculate_expire_date()
                current_transaction.status = Transaction.SUCCESS_PAYMENT,
                current_transaction.info = f" Success payment by refId = {ref_str} by user: {current_user.username}"
                current_transaction.save()

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

                # guardian permission library
                for course in current_plan.courses.all:
                    group, created = Group.objects.get_or_create(name=group_course_name(course.title))
                    assign_perm('fully_view_course', group, course)
                    current_user.groups.add(group)

                return render(request, 'payment_detail.html', {
                    'transaction': current_transaction,
                    'success': f'تراکنش شما با کد پیگیری {ref_str} با موفقیت انجام شد',
                })
            elif t_status == 101:
                return render(request, 'payment_detail.html', {
                    'transaction': current_transaction,
                    'info': 'این تراکنش قبلا ثبت شده است'
                })
            else:
                # return HttpResponse('Transaction failed.\nStatus: ' + str(
                #     req.json()['data']['message']
                # ))
                return render(request, 'payment_detail.html', {
                    'transaction': current_transaction,
                    'error': str(req.json()['data']['message'])
                })
        else:
            e_code = req.json()['errors']['code']
            e_message = req.json()['errors']['message']
            # return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")
            return render(request, 'payment_detail.html', {
                'transaction': current_transaction,
                'error': f"Error code: {e_code}, Error Message: {e_message}"
            })
    else:
        return render(request, 'payment_detail.html', {
            'transaction': current_transaction,
            'error': 'پرداخت با خطا مواجه شد / یا شما پرداخت را لغو کردید.'
        })
