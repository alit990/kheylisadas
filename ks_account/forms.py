import re

from captcha.fields import CaptchaField, CaptchaTextInput
from django import forms
from django.core import validators
from django.core.validators import RegexValidator

from ks_account.models import User


from django import forms
from django.core.validators import RegexValidator

from utility.faraz_sms import normalize_phone_number


# class LoginForm(forms.Form):
#     captcha_field = CaptchaField(
#         label='عبارت رو به رو را وارد کنید',
#     )
#     # captcha_field = CaptchaField(
#     #     label='عبارت رو به رو را وارد کنید',
#     #     widget=CaptchaTextInput(attrs={'id': "captcha_field"})
#     # )
#     username = forms.CharField(
#         label='نام کاربری',
#         widget=forms.TextInput(
#             attrs={'class': "form-control text-center",
#                    'id': "username"}
#         ),
#         validators=[
#             RegexValidator(regex='^[a-zA-Z0-9]*$', message='لطفاً تنها از حروف لاتین و اعداد استفاده کنید و فاصله وارد نکنید.'),
#             validators.MaxLengthValidator(20),
#         ]
#     )
#     password = forms.CharField(
#         label='کلمه عبور',
#         widget=forms.PasswordInput(
#             attrs={'class': "form-control text-center",
#                    'id': "password"}
#         ),
#         validators=[
#             validators.MaxLengthValidator(100),
#         ]
#     )
#     remember_me = forms.BooleanField(
#         label='مرا به خاطر بسپار',
#         required=False,
#         initial=True,  # فعال کردن پیش‌فرض
#         widget=forms.widgets.CheckboxInput(attrs={'class': 'checkbox-inline'}),
#         help_text=" با فعال کردن این گزینه، شما با بستن مرورگر از سایت خارج نمی شوید.",
#     )


class LoginForm(forms.Form):
    captcha_field = CaptchaField(
        label='عبارت رو به رو را وارد کنید',
    )
    username = forms.CharField(
        label='نام کاربری',
        max_length=11,  # طول دقیق شماره استاندارد
        widget=forms.TextInput(
            attrs={'class': "form-control text-center", 'id': "username", 'inputmode': "text"}
        ),
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9]*$',
                message='لطفاً تنها از حروف لاتین و اعداد استفاده کنید و فاصله وارد نکنید.'
            ),
        ]
    )
    password = forms.CharField(
        label='کلمه عبور',
        # max_length=11,  # طول دقیق شماره استاندارد
        widget=forms.PasswordInput(
            attrs={'class': "form-control text-center", 'id': "password", 'inputmode': "text"}
        ),

    )
    remember_me = forms.BooleanField(
        label='مرا به خاطر بسپار',
        required=False,
        initial=True,
        widget=forms.widgets.CheckboxInput(attrs={'class': 'checkbox-inline'}),
        help_text="با فعال کردن این گزینه، شما با بستن مرورگر از سایت خارج نمی‌شوید."
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # اگر ورودی شبیه شماره تلفن است، نرمال‌سازی کن
            if any(char.isdigit() for char in username):
                normalized = normalize_phone_number(username)
                if normalized and re.match(r'^0\d{10}$', normalized):
                    return normalized
            return username
        raise forms.ValidationError('نام کاربری نمی‌تواند خالی باشد.')

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            # اگر رمز شبیه شماره تلفن است، نرمال‌سازی کن
            if any(char.isdigit() for char in password):
                normalized = normalize_phone_number(password)
                if normalized and re.match(r'^0\d{10}$', normalized):
                    return normalized
            return password
        raise forms.ValidationError('کلمه عبور نمی‌تواند خالی باشد.')
class MobileInputForm(forms.Form):
    mobile_number = forms.CharField(
        max_length=11,  # طول دقیق شماره استاندارد
        label='شماره تلفن همراه',
        widget=forms.TextInput(
            attrs={
                'class': "form-control text-center",
                'id': "mobile",
                'maxlength': "11",
                'inputmode': "numeric",
                'style': "direction: ltr;"
            }
        )
    )

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')
        if mobile:
            normalized_mobile = normalize_phone_number(mobile)
            if normalized_mobile is None or len(normalized_mobile) != 11:
                raise forms.ValidationError('شماره همراه باید دقیقاً ۱۱ رقم باشد و با ۰ شروع شود.')
            if not re.match(r'^0\d{10}$', normalized_mobile):
                raise forms.ValidationError('شماره همراه معتبر نیست.')
            return normalized_mobile
        raise forms.ValidationError('شماره تلفن همراه نمی‌تواند خالی باشد.')

class ActivationForm(forms.Form):
    activation_code = forms.CharField(
        max_length=4,
        label=' کد فعالسازی',
        widget=forms.TextInput(
            attrs={'class': "form-control text-center", 'id': "activation_code"}
        ),
        validators=[
            RegexValidator(regex='^\d{4}$', message='لطفاً تنها 4 عدد وارد کنید.'),
            validators.MaxLengthValidator(4),
        ]
    )


class UsernameForm(forms.Form):
    username = forms.CharField(max_length=30,
                               label=' نام کاربری',
                               widget=forms.TextInput(
                                   attrs={'class': "form-control text-center",
                                          'id': "username"}),
                               validators=[
                                   RegexValidator(regex='^[a-zA-Z0-9]*$',
                                                  message='لطفاً تنها از حروف لاتین و اعداد استفاده کنید و فاصله وارد نکنید.'),
                                   validators.MinLengthValidator(5),
                               ]
                               )


class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
