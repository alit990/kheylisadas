import random
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import FormView
from guardian.shortcuts import assign_perm

from ks_account.forms import MobileInputForm, ActivationForm, UsernameForm, LoginForm
from ks_account.models import User, ActivityLog
from ks_category.models import Category
from ks_site.models import AccountSetting
from ks_subscription.models import Campaign, Payment, CTransaction, Transaction
from utility.choices import PaymentStatus
from utility.faraz_sms import standard_number, send_activation_sms, send_user_pass_sms, send_user_activate_sms, \
    send_new_campaign_sms
from utility.http_service import get_client_ip

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from utility.utils import group_subscription_name, group_course_name


#  ------------------------start admin views --------------------------------
def reset_user_password(request, id):
    user = get_object_or_404(User, pk=id)
    if request.method == 'POST':
        user.set_password(user.mobile)  # فرض بر این است که شماره موبایل در پروفایل کاربر ذخیره شده است
        user.save()
        messages.success(request, 'Password reset to mobile number successfully')
        return redirect('admin:index')
    context = {'user': user, 'title': 'Reset Password'}
    return render(request, 'admin/auth/user/reset_password.html', context)


def activate_user(request, id):
    user = get_object_or_404(User, pk=id)
    if request.method == 'POST':
        if not user.is_active:

            # ارسال پیامک
            if send_user_activate_sms(user.mobile, user.username, standard_number(user.mobile)):
                user.is_active = True
                user.username = standard_number(
                    user.mobile)  # فرض بر این است که شماره موبایل در پروفایل کاربر ذخیره شده است
                user.set_password(standard_number(user.mobile))  # تنظیم کلمه عبور به شماره موبایل
                user.save()
                messages.success(request, 'کاربر با موفقیت فعال شد و پیامک ارسال شد.')
            else:
                messages.error(request, 'کاربر فعال نشد و پیامک ارسال نشد. عملیات ناموفق')

        else:
            messages.info(request, 'کاربر از قبل فعال است.')
        return redirect('admin:index')
    context = {'user': user, 'title': 'فعال‌سازی کاربر'}
    return render(request, 'admin/auth/user/activate_user.html', context)


@login_required
def grant_campaign(request, id):
    user = get_object_or_404(User, pk=id)
    campaigns = Campaign.objects.filter(is_open=True, is_active=True)  # فقط کمپین‌های فعال و باز
    categories = Category.objects.all()  # همه دسته‌بندی‌ها (می‌توانید بر اساس نیاز فیلتر کنید)

    if request.method == 'POST':
        campaign_id = request.POST.get('campaign')
        category_id = request.POST.get('category')
        current_campaign = get_object_or_404(Campaign, id=campaign_id)
        current_category = get_object_or_404(Category, id=category_id)

        try:
            with transaction.atomic():
                # ابتدا اطلاعات اولیه برای ارسال پیامک آماده می‌شود
                campaign_duration = current_campaign.duration
                start_date = timezone.now()
                end_date = start_date.date() + timedelta(days=campaign_duration)

                # ارسال پیامک
                message_id = send_new_campaign_sms(
                    user.mobile,
                    current_campaign.name,
                    campaign_duration,
                    end_date
                )

                # اگر پیامک با موفقیت ارسال نشد، عملیات متوقف می‌شود
                if not message_id:
                    messages.error(request, "ارسال پیامک با خطا مواجه شد. اشتراک اعطا نشد.")
                    return redirect('admin:index')

                # اگر پیامک با موفقیت ارسال شد، ادامه عملیات
                # ایجاد پرداخت دستی
                new_payment = Payment.objects.create(
                    user=user,
                    method=Payment.CASH,
                    price=current_campaign.price,
                    type=Payment.CAMPAIGN,
                    is_paid=True,
                    status=PaymentStatus.PAID_NO_ERRORS,
                    payment_date=timezone.now(),
                    ref_code="MANUAL_GRANT"
                )

                # ایجاد CTransaction
                current_c_transaction = CTransaction.objects.create(
                    user=user,
                    campaign=current_campaign,
                    payment=new_payment,
                    category=current_category,
                    is_paid=True,
                    in_process=False,
                    start_date=start_date,
                    gift_day=current_campaign.campaign_gift,
                    status=CTransaction.STATUS_CODES["SUCCESS_PAYMENT"],
                    info=f"اعطای دستی کمپین توسط ادمین برای کاربر: {user.username}"
                )
                current_c_transaction.calculate_expire_date()
                current_c_transaction.save()

                # ایجاد Transaction جدید
                current_transaction = Transaction.objects.create(
                    user=user,
                    plan=None,
                    payment=new_payment,
                    is_paid=True,
                    in_process=False,
                    start_date=start_date,
                    status=Transaction.STATUS_CODES["SUCCESS_PAYMENT"],
                    info=f"اعطای دستی کمپین توسط ادمین برای کاربر: {user.username}"
                )

                # مدیریت Transaction قبلی
                if user.groups.filter(name=group_subscription_name()).exists():
                    old_transaction = Transaction.objects.filter(user=user, is_paid=True, is_expired=False).first()
                    if old_transaction and not old_transaction.is_expired_this:
                        remaining_time = old_transaction.end_date - timezone.now()
                        remaining_days = remaining_time.days
                        old_transaction.is_expired = True
                        old_transaction.save()
                        current_transaction.end_date = current_transaction.start_date.date() + timedelta(
                            days=current_campaign.duration + remaining_days)
                        current_transaction.save()
                    else:
                        current_transaction.end_date = current_transaction.start_date.date() + timedelta(
                            days=current_campaign.duration)
                        current_transaction.save()
                else:
                    current_transaction.end_date = current_transaction.start_date.date() + timedelta(
                        days=current_campaign.duration)
                    current_transaction.save()

                # اعطای مجوزها
                assign_perm('fully_view_campaign', user, current_campaign)

                # اضافه کردن کاربر به گروه اشتراک
                plan_group, created = Group.objects.get_or_create(name=group_subscription_name())
                user.groups.add(plan_group)

                # اعطای دسترسی به دوره‌های مرتبط با کمپین
                courses = current_campaign.courses.all()
                for course in courses:
                    group, created = Group.objects.get_or_create(name=group_course_name(course.title))
                    assign_perm('fully_view_course', group, course)
                    user.groups.add(group)

                messages.success(request, f'کمپین "{current_campaign.name}" با موفقیت به کاربر اعطا شد و پیامک ارسال شد.')
                return redirect('admin:index')

        except Exception as e:
            messages.error(request, f'خطا در اعطای کمپین: {str(e)}')
            return redirect('admin:index')

    context = {
        'user': user,
        'campaigns': campaigns,
        'categories': categories,
        'title': 'اعطای کمپین به کاربر'
    }
    return render(request, 'admin/auth/user/grant_campaign.html', context)



#  ===================== end admin views =====================================


class MobileRegisterView(FormView):
    template_name = 'mobile_register.html'
    form_class = MobileInputForm
    success_url = reverse_lazy('activation_view')

    def form_valid(self, form):
        try:
            mobile_number = form.cleaned_data.get('mobile_number')
            if self.request.user.is_authenticated:
                return redirect("/")

            user_ip = get_client_ip(self.request)
            mobile = mobile_number

            try:
                current_user = User.objects.get(mobile=standard_number(mobile))
                if current_user.is_active:
                    form.add_error('mobile_number', 'این شماره قبلا ثبت نام شده است.')
                    form.error_code = 'duplicate_number'
                    return self.form_invalid(form)
                else:
                    # User exists but is not active. Resend code.
                    current_user.mobile_active_code = random.randint(1085, 9985)
                    current_user.save()
                    if send_activation_sms(mobile=mobile, activation_code=current_user.mobile_active_code):
                        ActivityLog.objects.create(user=current_user, type=ActivityLog.SENT_ACTIVATION_SMS, ip=user_ip,
                                                   description="Activation code resent")
                        self.request.session['mobile_number'] = mobile_number
                        self.request.session['start_time'] = timezone.now().isoformat()
                        return super().form_valid(form)
                    else:
                        form.add_error('mobile_number', 'در ارسال کد فعالسازی خطایی رخ داده است.')
                        return self.form_invalid(form)

            except User.DoesNotExist:
                # New user
                current_user = User.objects.create_user(username=standard_number(mobile),
                                                        password=standard_number(mobile),
                                                        mobile=standard_number(mobile))
                current_user.mobile_active_code = random.randint(1085, 9985)
                current_user.is_active = False  # Important: Set is_active to False initially
                current_user.save()

                if send_activation_sms(mobile=mobile, activation_code=current_user.mobile_active_code):
                    ActivityLog.objects.create(user=current_user, type=ActivityLog.SENT_ACTIVATION_SMS, ip=user_ip,
                                               description="New user created")
                    self.request.session['mobile_number'] = mobile_number
                    self.request.session['start_time'] = timezone.now().isoformat()
                    return super().form_valid(form)
                else:
                    form.add_error('mobile_number', 'در ارسال کد فعالسازی خطایی رخ داده است.')
                    return self.form_invalid(form)
        except Exception as e:
            # ثبت خطای کلی
            ActivityLog.objects.create(user=None, type=ActivityLog.REGISTER_FAILED_UNKNOWN,
                                       ip=get_client_ip(self.request),
                                       description=f"Unknown error in MobileRegisterView: {e}")
            form.add_error('mobile_number',
                           'خطایی در ثبت نام رخ داده است. لطفا دوباره تلاش کنید.')  # پیام مناسب به کاربر
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['setting'] = AccountSetting.objects.filter(is_main_setting=True).first()
        context['title'] = "ثبت نام"
        return context

    def get_initial(self):
        initial = super().get_initial()
        mobile_number = self.request.session.get('mobile_number')
        if mobile_number:
            initial['mobile_number'] = mobile_number
        return initial


class ActivationView(FormView):
    template_name = 'activation.html'
    form_class = ActivationForm
    success_url = reverse_lazy('plans_list')

    def form_valid(self, form):
        activation_code = form.cleaned_data.get('activation_code')
        mobile = self.request.session.get('mobile_number')

        if mobile is None:
            form.add_error('activation_code', 'متاسفانه خطایی رخ داده است. شماره موبایل یافت نشد.')
            return self.form_invalid(form)

        start_time_str = self.request.session.get('start_time')
        if start_time_str is None:
            form.add_error('activation_code', 'متاسفانه خطایی رخ داده است. زمان شروع یافت نشد.')
            return self.form_invalid(form)
        start_time = timezone.datetime.fromisoformat(start_time_str)
        expiration_time = start_time + timezone.timedelta(minutes=3)

        if timezone.now() > expiration_time:
            form.add_error('activation_code', 'کد فعالسازی منقضی شده است.')
            return self.form_invalid(form)
        try:
            user = User.objects.get(mobile=standard_number(mobile))  # Get user based on mobile number
        except User.DoesNotExist:
            user = None  # If user not found, set user to None

        if user is None:  # Handle User not found case
            ActivityLog.objects.create(user=None, type=ActivityLog.ACTIVATION_FAILED_USER_NOT_FOUND,
                                       ip=get_client_ip(self.request), description="User not found during activation")
            form.add_error('activation_code', 'متاسفانه خطایی رخ داده است. کاربر یافت نشد.')
            return self.form_invalid(form)

        try:
            # user = User.objects.get(mobile=standard_number(mobile))  # Get user based on mobile number
            ActivityLog.objects.create(user=user, type=ActivityLog.SENT_ACTIVATION_SMS_VERIFIED,
                                       ip=get_client_ip(self.request),
                                       description="Activation code entered")

            if int(activation_code) == user.mobile_active_code:
                user.is_active = True
                user.username = standard_number(mobile)
                user.set_password(standard_number(mobile))
                user.save()

                sms_sent = send_user_pass_sms(mobile=standard_number(mobile), username=user.username,
                                              password=standard_number(mobile))
                if not sms_sent:
                    ActivityLog.objects.create(user=user, type=ActivityLog.SMS_DELIVERY_FAILED,
                                               ip=get_client_ip(self.request),
                                               description="Failed to send user password SMS")
                    messages.error(self.request, 'خطا در ارسال پیامک رمز عبور. لطفا با پشتیبانی تماس بگیرید.')
                    return self.form_invalid(form)

                user_ip = get_client_ip(self.request)
                self.request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
                activity_log_register: ActivityLog = ActivityLog(user=user, type=ActivityLog.REGISTER_SUCCESS,
                                                                 ip=user_ip)
                activity_log_login: ActivityLog = ActivityLog(user=user, type=ActivityLog.LOGIN_SUCCESS, ip=user_ip)
                activity_log_register.save()
                activity_log_login.save()
                login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')

                # messages.success(self.request, 'ثبت نام با موفقیت انجام شد.',
                #                  extra_tags=f'from_registration username={user.username}|||mobile={user.mobile}')
                messages.success(self.request, 'ثبت نام با موفقیت انجام شد.', extra_tags='new_user')

                del self.request.session['mobile_number']
                del self.request.session['start_time']

                return redirect(self.success_url)
            else:
                ActivityLog.objects.create(user=user, type=ActivityLog.ACTIVATION_FAILED_INVALID_CODE_ENTERED,
                                           ip=get_client_ip(self.request),
                                           description="Invalid activation code entered by user")
                form.add_error('activation_code', 'کد فعالسازی صحیح نیست.')
                return self.form_invalid(form)

        except ValueError:
            ActivityLog.objects.create(user=user, type=ActivityLog.ACTIVATION_FAILED_INVALID_CODE,
                                       ip=get_client_ip(self.request), description="Invalid activation code format")
            form.add_error('activation_code', 'کد فعالسازی وارد شده نامعتبر است.')
            return self.form_invalid(form)
        except Exception as e:  # ActivationCodeExpired is caught by this
            ActivityLog.objects.create(user=user, type=ActivityLog.ACTIVATION_FAILED_EXPIRED_CODE if "expired" in str(
                e).lower() else ActivityLog.ACTIVATION_FAILED_UNKNOWN, ip=get_client_ip(self.request),
                                       description=f"Activation error: {e}")
            form.add_error('activation_code', 'خطایی در فعالسازی رخ داده است. لطفا دوباره تلاش کنید.')
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['setting'] = AccountSetting.objects.filter(is_main_setting=True).first()
        context['start_time'] = self.request.session.get('start_time')  # Pass start_time to template
        return context


# No more UsernameView

class ForgetPassMobileView(FormView):
    template_name = 'forget_pass.html'
    form_class = MobileInputForm
    success_url = reverse_lazy('forget_pass_activation_view')

    def form_valid(self, form):
        # send activation code
        mobile_number = form.cleaned_data.get('mobile_number')
        if self.request.user.is_authenticated:
            return redirect("/")
        else:
            user_ip = get_client_ip(self.request)
            mobile = mobile_number
            self.request.session['mobile_number'] = mobile_number
            try:
                current_user = User.objects.filter(mobile=standard_number(mobile)).first()
            except:
                form.add_error(" کاربری با این مشخصات یافت نشد! ")
                return self.form_invalid(form)

            limit_minutes_ago = datetime.now() - timedelta(minutes=15)
            sms_count_in_last_limit_min = ActivityLog.objects.filter(
                Q(create_date__gte=limit_minutes_ago) & Q(user_id=current_user.id) &
                (Q(type=ActivityLog.SENT_ACTIVATION_SMS) | Q(type=ActivityLog.SENT_RESET_PASSWORD_SMS))
            ).count()

            if sms_count_in_last_limit_min < 6:
                current_user.mobile_active_code = random.randint(9008, 9888)
                current_user.save()
                if send_activation_sms(mobile=mobile, activation_code=current_user.mobile_active_code):
                    activity_log: ActivityLog = ActivityLog(user=current_user,
                                                            type=ActivityLog.SENT_RESET_PASSWORD_SMS,
                                                            ip=user_ip, description="forget pass sms sent")
                    activity_log.save()
                    # set the start time in the session
                    start_time = timezone.now()
                    start_time_str = start_time.isoformat()  # convert datetime to string
                    self.request.session['start_time'] = start_time_str
                    return super().form_valid(form)
                else:
                    form.add_error('mobile_number', 'در ارسال کد فعالسازی خطایی رخ داده است.')
                    return self.form_invalid(form)
            else:
                current_user.save()
                form.add_error('mobile_number',
                               'پیام های ارسالی شما بیش از اندازه بوده است. لطفا دقایقی دیگر تلاش کنید.')
                return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['setting'] = AccountSetting.objects.filter(is_main_setting=True).first()
        context['title'] = "فراموشی رمز"
        return context

    def get_initial(self):
        initial = super().get_initial()
        mobile_number = self.request.session.get('mobile_number')
        if mobile_number:
            initial['mobile_number'] = mobile_number
        return initial


class ForgetPassActivationView(FormView):
    template_name = 'forget_pass_activation.html'
    form_class = ActivationForm
    success_url = reverse_lazy('plans_list')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            redirect("home_page")
        else:
            # check activation code
            user_code = form.cleaned_data.get('activation_code')
            mobile = self.request.session.get('mobile_number')
            if mobile is None:
                print("mobile number not found in session")
                # handle the case where mobile_number is not in the session
                # form.add_error('activation_code', 'متاسفانه خطایی رخ داده است.')
                # return self.form_invalid(form)
                redirect("forget_pass_view")
            else:
                # use mobile_number
                # use mobile_number to verify the activation code
                try:
                    user = User.objects.filter(mobile__contains=mobile).first()
                    if int(user_code) == user.mobile_active_code:
                        user.set_password(standard_number(mobile))  # ==> 09158100000
                        user.is_active = True
                        user.save()
                        send_user_pass_sms(mobile=standard_number(mobile), username=user.username,
                                           password=standard_number(mobile))
                        # login
                        user_ip = get_client_ip(self.request)
                        # the purpose is checking remember me checkbox is checked or not.
                        self.request.session.set_expiry(60 * 60 * 24 * 30)  # Here we extend session for 10 days.
                        activity_log_reset_pass = ActivityLog(user=user, type=ActivityLog.SENT_RESET_PASSWORD_SMS,
                                                              ip=user_ip)
                        activity_log_login = ActivityLog(user=user, type=ActivityLog.LOGIN_SUCCESS,
                                                         ip=user_ip)
                        activity_log_reset_pass.save()
                        activity_log_login.save()
                        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
                        # messages.success(self.request,
                        #                  f" عملیات با موفقیت انجام شد. نام کاربری شما "
                        #                  f"{user.username}"
                        #                  f" و کلمه عبور شما "
                        #                  f" شماره موبایلتان "
                        #                  f"{user.mobile}"
                        #                  f" است. شما در هر لحظه میتوانید با مراجعه به پنل کاربری، "
                        #                  f"کلمه عبور خود را تغییر دهید. ")
                        # return redirect('success_page')
                        messages.success(self.request, 'ثبت نام با موفقیت انجام شد.', extra_tags='new_user')

                        del self.request.session['mobile_number']
                        del self.request.session['start_time']

                        return redirect(self.success_url)

                except:
                    form.add_error('activation_code', 'کد فعالسازی صحیح نیست.')
                    return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['setting'] = AccountSetting.objects.filter(is_main_setting=True).first()
        # pass the start time to the template
        context['start_time'] = self.request.session.get('start_time')
        return context


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home_page')

        login_form = LoginForm()
        setting = AccountSetting.objects.filter(is_main_setting=True).first()
        next_url = request.GET.get('next', '/')  # مقدار پیش‌فرض '/' اگر در GET نباشد
        context = {
            'login_form': login_form,
            'setting': setting,
            'next_url': next_url,
        }
        return render(request, 'login.html', context)

    def post(self, request):
        login_form = LoginForm(request.POST)
        user_ip = get_client_ip(request)
        next_url = request.POST.get('next', request.GET.get('next', '/'))  # اولویت: POST، سپس GET، سپس '/'

        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            remember_me = login_form.cleaned_data.get('remember_me')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    if remember_me:
                        request.session.set_expiry(60 * 60 * 24 * 30)  # 30 روز
                    else:
                        request.session.set_expiry(0)  # بسته شدن مرورگر

                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    ActivityLog.objects.create(user=user, type=ActivityLog.LOGIN_SUCCESS, ip=user_ip)

                    if not next_url or next_url.startswith('/logout/') or next_url.startswith('/password_reset/') or next_url.startswith('/password_change/') or next_url == "/header":
                        next_url = '/'
                    return redirect(next_url)
                else:
                    login_form.add_error('username', 'حساب کاربری شما غیر فعال است.')
                    ActivityLog.objects.create(user=None, type=ActivityLog.LOGIN_FAILED_USER_NOT_FOUND, ip=user_ip)
            else:
                user = User.objects.filter(username=username).first()
                if user:
                    login_form.add_error('password', 'کلمه عبور اشتباه است.')
                    ActivityLog.objects.create(user=user, type=ActivityLog.LOGIN_FAILED_INCORRECT_PASSWORD, ip=user_ip)
                else:
                    login_form.add_error('username', 'کاربری با این مشخصات یافت نشد.')
                    ActivityLog.objects.create(user=None, type=ActivityLog.LOGIN_FAILED_USER_NOT_FOUND, ip=user_ip)

        # همیشه context را با next_url برگردانیم
        setting = AccountSetting.objects.filter(is_main_setting=True).first()
        context = {
            'login_form': login_form,
            'setting': setting,
            'next_url': next_url if next_url else '/',  # اطمینان از وجود مقدار
        }
        return render(request, 'login.html', context)#     def get(self, request):
#         if request.user.is_authenticated:
#             return redirect('home_page')
#
#         login_form = LoginForm()
#         setting = AccountSetting.objects.filter(is_main_setting=True).first()
#         next_url = request.GET.get('next')  # Get next_url from query parameters
#         context = {
#             'login_form': login_form,
#             'setting': setting,
#             'next_url': next_url,  # Add next_url to context
#         }
#         return render(request, 'login.html', context)
#
#     def post(self, request):
#         login_form = LoginForm(request.POST)
#         user_ip = get_client_ip(request)
#
#         if login_form.is_valid():
#             username = login_form.cleaned_data.get('username')
#             password = login_form.cleaned_data.get('password')
#             remember_me = login_form.cleaned_data.get('remember_me')
#
#             user = authenticate(request, username=username, password=password)
#
#             if user is not None:
#                 if user.is_active:
#                     if remember_me:
#                         request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
#                     else:
#                         request.session.set_expiry(0)  # Session expires on browser close
#
#                     login(request, user, backend='django.contrib.auth.backends.ModelBackend')
#
#                     ActivityLog.objects.create(user=user, type=ActivityLog.LOGIN_SUCCESS, ip=user_ip)
#
#                     next_url = request.POST.get('next', '/')  # Get next URL from POST data
#                     if not next_url or next_url.startswith('/logout/') or next_url.startswith(
#                             '/password_reset/') or next_url.startswith('/password_change/')\
#                             or next_url == "/header":
#                         next_url = '/'  # اگر next_url معتبر نبود، به صفحه اصلی redirect کن
#
#                     return JsonResponse({'success': True, 'redirect_url': next_url})
#
#                 else:
#                     login_form.add_error('username', 'حساب کاربری شما غیر فعال است.')
#                     ActivityLog.objects.create(user=None, type=ActivityLog.LOGIN_FAILED_USER_NOT_FOUND, ip=user_ip)
#                     return JsonResponse({'success': False, 'errors': login_form.errors.as_json()})
#
#             else:
#                 # کاربر وجود دارد، اما رمز عبور اشتباه است
#                 user = User.objects.filter(username=username).first()  # دریافت کاربر از پایگاه داده
#                 if user:
#                     login_form.add_error('password', 'کلمه عبور اشتباه است.')  # اضافه کردن خطا به فیلد password
#                     ActivityLog.objects.create(user=user, type=ActivityLog.LOGIN_FAILED_INCORRECT_PASSWORD, ip=user_ip)
#                 else:
#                     login_form.add_error('username', 'کاربری با این مشخصات یافت نشد.')
#                     ActivityLog.objects.create(user=None, type=ActivityLog.LOGIN_FAILED_USER_NOT_FOUND, ip=user_ip)
#
#                 return JsonResponse({'success': False, 'errors': login_form.errors.as_json()})
#
#         else:
#             errors = {}
#             for field, error_messages in login_form.errors.items():
#                 messages = []
#                 for error in error_messages:
#                     messages.append(str(error))  # تبدیل شیء خطا به رشته
#                 errors[field] = messages
#
#             # بررسی خطا برای فیلد captcha_field و ارسال پیام مناسب
#             if 'captcha_field' in login_form.errors:
#                 captcha_errors = login_form.errors['captcha_field']
#                 if captcha_errors:  # اگر خطاها خالی نبودند
#                     errors['id_captcha_field_1'] = [str(error) for error in
#                                                captcha_errors]  # لیست خطاها را به رشته تبدیل میکنیم
#                 else:
#                     errors['id_captcha_field_1'] = ["کد کپچا وارد نشده است."]  # پیام مناسب برای خالی بودن فیلد
#
#             return JsonResponse({'success': False, 'errors': errors})
#         # else:
#         #     if 'captcha_field' in login_form.errors and not request.POST.get('captcha_field'):
#         #         ActivityLog.objects.create(user=None, type=ActivityLog.LOGIN_FAILED_INCORRECT_CAPTCHA, ip=user_ip)
#         #     return JsonResponse({'success': False, 'errors': login_form.errors.as_json()})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('/')
