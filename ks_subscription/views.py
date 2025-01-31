from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, FormView
from django.views.generic.edit import FormMixin
from guardian.shortcuts import assign_perm

from kheylisadas import settings
from ks_account.decorators import signup_required
from ks_account.models import User
from ks_audio.models import Audio, AudioWeek
from ks_site.models import SiteSetting
from ks_subscription.forms import GiftCodeForm
from ks_subscription.models import Plan, Payment, Transaction, GiftPlan
import time
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse, HttpResponse, HttpResponseForbidden
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, render
import requests
import json

from utility.choices import PaymentStatus
from utility.faraz_sms import send_new_subscription_sms
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

@login_required
def cancel_pending_payments(request: HttpRequest):
    current_user: User = request.user
    # Mark all in-process transactions as not in process
    for transaction in Transaction.objects.filter(user_id=current_user.id, in_process=True):
        transaction.in_process = False
        transaction.save()

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

    # Redirect if the price is zero
    if total_price == 0:
        return redirect(reverse('plan_detail'))

    # Check for active subscription and transactions
    if current_user.groups.filter(name=group_subscription_name()).exists():
        if Transaction.objects.filter(user_id=current_user.id, is_paid=True, is_expired=False).exists():
            transaction = Transaction.objects.filter(user_id=current_user.id, is_paid=True, is_expired=False).first()
            if not transaction.is_expired_this:
                messages.error(request, "You currently have an active subscription and do not need a new one.")
                return redirect('failure_page')

    # Check for pending transactions in the last 2 minutes
    limit_minutes_ago = datetime.now() - timedelta(minutes=2)
    if Transaction.objects.filter(
            Q(try_date__gte=limit_minutes_ago) & Q(user=current_user) & Q(in_process=True)).count() > 0:
        message_tags = f'pending_payment'
        messages.error(request, "شما یک عملیات پرداخت در حال انجام دارید. به همین دلیل عملیات ناموفق بود.",
                       extra_tags=message_tags)
        return redirect('failure_page')

    # Mark old transactions as not in process
    for transaction in Transaction.objects.filter(user_id=current_user.id, in_process=True):
        transaction.in_process = False
        transaction.save()

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

    # Create callback URL
    callback_url = request.build_absolute_uri(reverse('verify_payment'))

    # Prepare data for ZarinPal request
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
                current_transaction.payment = new_payment
                current_transaction.status = Transaction.STATUS_CODES["BEFORE_PAYMENT"]
                current_transaction.info = 'No errors - NOT PAID'
                current_transaction.save()
                return redirect(ZP_API_STARTPAY + authority)  # Redirect to ZarinPal payment gateway
            else:
                error_code = response_json['Status']
                new_payment.status = PaymentStatus.PAYMENT_ERROR
                new_payment.error = f"Error code: {error_code}"
                new_payment.save()
                current_transaction.status = Transaction.STATUS_CODES["ERROR_BEFORE_PAYMENT"]
                current_transaction.info = f"Error code: {error_code}"
                current_transaction.save()
                return HttpResponse(f"Error code: {error_code}")
        else:
            return HttpResponse(f"Request failed with status code: {response.status_code}")

    except requests.exceptions.Timeout:
        return HttpResponse("Request timed out.")
    except requests.exceptions.ConnectionError:
        return HttpResponse("Connection error.")
    except Exception as e:
        return HttpResponse(f"An unexpected error occurred: {e}")


@login_required
def verify_payment(request: HttpRequest):
    current_user: User = request.user
    current_transaction = Transaction.objects.filter(user_id=current_user.id, in_process=True).first()

    if not current_transaction:
        return HttpResponse("Transaction not found.")

    current_payment = Payment.objects.filter(id=current_transaction.payment_id).first()
    current_plan = Plan.objects.filter(id=current_transaction.plan_id).first()
    total_price = current_plan.price

    t_authority = request.GET.get('Authority')
    if request.GET.get('Status') == 'OK':
        req_header = {"accept": "application/json", "content-type": "application/json"}
        req_data = {
            "MerchantID": MERCHANT,
            "Amount": total_price,  # Rial to Toman conversion
            "Authority": t_authority
        }
        req = requests.post(ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
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
                current_transaction.info = f"Success payment by refId = {ref_str} by user: {current_user.username}"
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
                current_transaction.in_process = False
                current_transaction.save()
                return render(request, 'payment_detail.html', {
                    'transaction': current_transaction,
                    'info': 'این تراکنش قبلا ثبت شده است'
                })

            else:
                current_transaction.in_process = False
                current_transaction.save()
                return render(request, 'payment_detail.html', {
                    'transaction': current_transaction,
                    'error': str(response_data['Status'])
                })
        else:
            e_code = response_data.get('errors', {}).get('code', 'unknown')
            e_message = response_data.get('errors', {}).get('message', 'Unknown error')
            return render(request, 'payment_detail.html', {
                'transaction': current_transaction,
                'error': f"Error code: {e_code}, Error Message: {e_message}"
            })
    else:
        current_transaction.in_process = False
        current_transaction.save()
        return render(request, 'payment_detail.html', {
            'transaction': current_transaction,
            'error': 'پرداخت با خطا مواجه شد / یا شما پرداخت را لغو کردید.'
        })
