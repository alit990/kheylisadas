import random
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import login, logout
from django.db.models import Q
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import FormView

from ks_account.forms import MobileInputForm, ActivationForm, UsernameForm, LoginForm
from ks_account.models import User, ActivityLog
from ks_site.models import AccountSetting
from utility.faraz_sms import standard_number, send_activation_sms, send_user_pass_sms
from utility.http_service import get_client_ip


class MobileRegisterView(FormView):
    template_name = 'mobile_register.html'
    form_class = MobileInputForm
    success_url = reverse_lazy('activation_view')

    def form_valid(self, form):
        # send activation code
        mobile_number = form.cleaned_data.get('mobile_number')
        if self.request.user.is_authenticated:
            return redirect("/")
        else:
            user_ip = get_client_ip(self.request)
            mobile = mobile_number
            self.request.session['mobile_number'] = mobile_number
            print(user_ip, mobile)
            current_user, created = User.objects.get_or_create(
                mobile=standard_number(mobile),
                defaults={'username': standard_number(mobile),
                          'mobile_active_code': random.randint(1085, 9985),
                          'is_active': False}, )
            limit_minutes_ago = datetime.now() - timedelta(minutes=15)
            sms_count_in_last_limit_min = ActivityLog.objects.filter(
                Q(create_date__gte=limit_minutes_ago) & Q(user=current_user)
                & Q(type=ActivityLog.SENT_ACTIVATION_SMS)).count()
            if sms_count_in_last_limit_min < 4:
                if created:
                    current_user.save()
                    if send_activation_sms(mobile=mobile, activation_code=current_user.mobile_active_code):
                        activity_log: ActivityLog = ActivityLog(user=current_user,
                                                                type=ActivityLog.SENT_ACTIVATION_SMS,
                                                                ip=user_ip, description="user is now created")
                        activity_log.save()
                        self.request.session['mobile_number'] = mobile_number

                        # set the start time in the session
                        start_time = timezone.now()
                        start_time_str = start_time.isoformat()  # convert datetime to string
                        self.request.session['start_time'] = start_time_str

                        return redirect('activation_view')
                    else:
                        form.add_error('mobile_number', 'در ارسال کد فعالسازی خطایی رخ داده است.')
                        return self.form_invalid(form)
                else:

                    if current_user.is_active:
                        form.add_error('mobile_number', 'شماره تلفن شما قبلا فعال شده است.')
                        return self.form_invalid(form)
                    else:
                        current_user.mobile_active_code = random.randint(1085, 9985)
                        current_user.save()
                        if send_activation_sms(mobile=mobile, activation_code=current_user.mobile_active_code):
                            activity_log: ActivityLog = ActivityLog(user=current_user,
                                                                    type=ActivityLog.SENT_ACTIVATION_SMS,
                                                                    ip=user_ip, description="user was already exists")
                            # set the start time in the session
                            start_time = timezone.now()
                            start_time_str = start_time.isoformat()  # convert datetime to string
                            self.request.session['start_time'] = start_time_str

                            activity_log.save()
                            return super().form_valid(form)
                        else:
                            form.add_error('mobile_number', 'در ارسال کد فعالسازی خطایی رخ داده است.')
                            return self.form_invalid(form)
            else:
                form.add_error('mobile_number', 'پیام های ارسالی شما بیش از اندازه بوده است.')
                return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['setting'] = AccountSetting.objects.filter(is_main_setting=True).first()
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
    success_url = reverse_lazy('username_view')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            redirect("/")
        else:
            # check activation code
            activation_code = form.cleaned_data.get('activation_code')
            mobile_number = self.request.session.get('mobile_number')
            if mobile_number is None:
                print("mobile number not found in session")
                form.add_error('activation_code', 'متاسفانه خطایی رخ داده است.')
                return self.form_invalid(form)
                # handle the case where mobile_number is not in the session
            else:
                # get the start time from the session
                start_time_str = self.request.session.get('start_time')
                start_time = timezone.datetime.fromisoformat(start_time_str)
                # calculate the expiration time
                expiration_time = start_time + timezone.timedelta(minutes=3)
                # check if the current time is past the expiration time
                if timezone.now() > expiration_time:
                    # the code has expired
                    form.add_error('activation_code', 'کد فعالسازی منقضی شده است.')
                    return self.form_invalid(form)
                # use mobile_number
                # use mobile_number to verify the activation code
                mobile = mobile_number
                user_code = activation_code
                try:
                    user = User.objects.filter(mobile__contains=mobile, is_active=False).first()
                    if int(user_code) == user.mobile_active_code:
                        return redirect('username_view')
                    else:
                        form.add_error('activation_code', 'کد فعالسازی صحیح نیست.')
                        return self.form_invalid(form)
                except:
                    form.add_error('activation_code', 'کد فعالسازی صحیح نیست.')
                    return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['setting'] = AccountSetting.objects.filter(is_main_setting=True).first()
        # pass the start time to the template
        context['start_time'] = self.request.session.get('start_time')
        return context


class UsernameView(FormView):
    template_name = 'username.html'
    form_class = UsernameForm
    success_url = reverse_lazy('success_view')

    def form_valid(self, form):
        # create user
        mobile_number = self.request.session.get('mobile_number')
        # use mobile_number to create the user
        mobile = mobile_number
        username = form.cleaned_data.get('username')

        print(mobile, username)
        user: User = User.objects.filter(mobile__contains=standard_number(mobile)).first()
        exist_username: bool = User.objects.filter(username__exact=username).exists()
        if exist_username:
            form.add_error('username', 'این نام کاربری در دسترسی نیست.')
            return self.form_invalid(form)
        else:
            user.username = username
            user.set_password(standard_number(mobile))  # ==> 09158100000
            user.is_active = True
            user.save()
            send_user_pass_sms(mobile=standard_number(mobile), username=username, password=standard_number(mobile))
            # login
            user_ip = get_client_ip(self.request)
            # but the purpose is checking remember me checkbox is checked or not.
            self.request.session.set_expiry(60 * 60 * 24 * 10)  # Here we extend session for 10 days.
            activity_log_register: ActivityLog = ActivityLog(user=user, type=ActivityLog.REGISTER_SUCCESS,
                                                             ip=user_ip)
            activity_log_login: ActivityLog = ActivityLog(user=user, type=ActivityLog.LOGIN_SUCCESS, ip=user_ip)
            activity_log_register.save()
            activity_log_login.save()
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(self.request,
                             f" ثبت نام شما با موفقیت انجام شد. نام کاربری شما {user.username} و کلمه عبور شما "
                             f" شماره موبایل شما {user.mobile} است. ")
            return redirect('success_page')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['setting'] = AccountSetting.objects.filter(is_main_setting=True).first()
        return context


class ForgetPassMobileView(FormView):
    template_name = 'mobile_register.html'
    form_class = MobileInputForm
    success_url = reverse_lazy('activation_view')

    def form_valid(self, form):
        # send activation code
        mobile_number = form.cleaned_data.get('mobile_number')
        if self.request.user.is_authenticated:
            return redirect("/")
        else:
            user_ip = get_client_ip(self.request)
            mobile = mobile_number
            self.request.session['mobile_number'] = mobile_number
            print(user_ip, mobile)
            try:
                current_user = User.objects.filter(mobile=standard_number(mobile))
            except:
                form.add_error(" کاربری با این مشخصات یافت نشد! ")
                return self.form_invalid(form)

            limit_minutes_ago = datetime.now() - timedelta(minutes=15)
            sms_count_in_last_limit_min = ActivityLog.objects.filter(
                Q(create_date__gte=limit_minutes_ago) & Q(user=current_user)
                & Q(type=ActivityLog.SENT_ACTIVATION_SMS)
                | Q(type=ActivityLog.SENT_RESET_PASSWORD_SMS)).count()
            if sms_count_in_last_limit_min < 4:
                current_user.mobile_active_code = random.randint(9008, 9888)
                current_user.save()
                if send_activation_sms(mobile=mobile, activation_code=current_user.mobile_active_code):
                    activity_log: ActivityLog = ActivityLog(user=current_user,
                                                            type=ActivityLog.SENT_RESET_PASSWORD_SMS,
                                                            ip=user_ip, description="forget pass sms sent")
                    activity_log.save()
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
        return context

    def get_initial(self):
        initial = super().get_initial()
        mobile_number = self.request.session.get('mobile_number')
        if mobile_number:
            initial['mobile_number'] = mobile_number
        return initial


class ForgetPassActivationView(FormView):
    template_name = 'activation.html'
    form_class = ActivationForm
    success_url = reverse_lazy('home_page')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            redirect("home_page")
        else:
            # check activation code
            activation_code = form.cleaned_data.get('activation_code')
            mobile_number = self.request.session.get('mobile_number')
            if mobile_number is None:
                print("mobile number not found in session")
                # handle the case where mobile_number is not in the session
                # form.add_error('activation_code', 'متاسفانه خطایی رخ داده است.')
                # return self.form_invalid(form)
                redirect("forget_pass_view")
            else:
                # use mobile_number
                # use mobile_number to verify the activation code
                mobile = mobile_number
                user_code = activation_code
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
                        self.request.session.set_expiry(60 * 60 * 24 * 10)  # Here we extend session for 10 days.
                        activity_log_reset_pass = ActivityLog(user=user, type=ActivityLog.SENT_RESET_PASSWORD_SMS,
                                                              ip=user_ip)
                        activity_log_login = ActivityLog(user=user, type=ActivityLog.LOGIN_SUCCESS,
                                                         ip=user_ip)
                        activity_log_reset_pass.save()
                        activity_log_login.save()
                        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
                        messages.success(self.request,
                                         f" عملیات با موفقیت انجام شد. نام کاربری شما "
                                         f"{user.username}"
                                         f" و کلمه عبور شما "
                                         f" شماره موبایلتان "
                                         f"{user.mobile}"
                                         f" است. شما در هر لحظه میتوانید با مراجعه به پنل کاربری، "
                                         f"کلمه عبور خود را تغییر دهید. ")
                        return redirect('success_page')

                except:
                    form.add_error('activation_code', 'کد فعالسازی صحیح نیست.')
                    return self.form_invalid(form)


class LoginView(View):
    next = ""

    def get(self, request):
        if request.user.is_authenticated:
            redirect('home_page')
        # next = request.GET.get('next')
        # print("befor next is ",next)
        login_form = LoginForm()
        setting = AccountSetting.objects.filter(is_main_setting=True).first()
        context = {
            # 'next': next,
            'login_form': login_form,
            'setting': setting
        }

        return render(request, 'login.html', context)

    def post(self, request: HttpRequest):
        login_form = LoginForm(request.POST)
        user_ip = get_client_ip(self.request)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            remember_me = login_form.cleaned_data.get('remember_me')
            user: User = User.objects.filter(username__exact=username).first()
            if user is not None:
                if not user.is_active:
                    login_form.add_error('username', 'حساب کاربری شما غیر فعال است. لطفا با پشتیبانی سایت تماس بگیرید.')
                else:
                    is_password_correct = user.check_password(password)
                    if is_password_correct:
                        if remember_me:
                            # but the purpose is checking remember me checkbox is checked or not.
                            request.session.set_expiry(60 * 60 * 24 * 20)  # Here we extend session for 20 days.
                        else:
                            # This part of code means, close session when browser is closed.
                            request.session.set_expiry(0)
                        activity_log: ActivityLog = ActivityLog(user=user, type=ActivityLog.LOGIN_SUCCESS, ip=user_ip)
                        activity_log.save()
                        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                        next = request.POST.get('next', '/')
                        print(next)
                        if next == "" or next == "/header":
                            print('next is empty')
                            return HttpResponseRedirect('/')
                        else:
                            print('next is ', next)
                            return HttpResponseRedirect(next)
                        # return redirect('/')
                    else:
                        activity_log: ActivityLog = ActivityLog(user=user,
                                                                type=ActivityLog.LOGIN_FAILED_INCORRECT_PASSWORD,
                                                                ip=user_ip)
                        activity_log.save()
                        login_form.add_error('username', 'کلمه عبور اشتباه است')
            else:
                login_form.add_error('username', 'کاربری با مشخصات وارد شده یافت نشد')
        else:  # if form is not valid
            if login_form.cleaned_data.get('captcha_field') is None:
                if login_form.cleaned_data.get('username'):
                    username = login_form.cleaned_data.get('username')
                    user: User = User.objects.filter(username__exact=username).first()
                    activity_log: ActivityLog = ActivityLog(user=user,
                                                            type=ActivityLog.LOGIN_FAILED_INCORRECT_CAPTCHA,
                                                            ip=user_ip)
                    activity_log.save()
        setting = AccountSetting.objects.filter(is_main_setting=True).first()
        context = {
            'login_form': login_form,
            'setting': setting
        }

        return render(request, 'login.html', context)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('/')
