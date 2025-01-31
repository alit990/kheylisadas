from captcha.fields import CaptchaField
from django import forms
from django.core import validators
from django.core.validators import RegexValidator

from ks_account.models import User


from django import forms
from django.core.validators import RegexValidator

class LoginForm(forms.Form):
    captcha_field = CaptchaField(
        label='عبارت رو به رو را وارد کنید',
    )
    username = forms.CharField(
        label='نام کاربری',
        widget=forms.TextInput(
            attrs={'class': "form-control text-center",
                   'id': "username"}
        ),
        validators=[
            RegexValidator(regex='^[a-zA-Z0-9]*$', message='لطفاً تنها از حروف لاتین و اعداد استفاده کنید و فاصله وارد نکنید.'),
            validators.MaxLengthValidator(20),
        ]
    )
    password = forms.CharField(
        label='کلمه عبور',
        widget=forms.PasswordInput(
            attrs={'class': "form-control text-center",
                   'id': "password"}
        ),
        validators=[
            validators.MaxLengthValidator(100),
        ]
    )
    remember_me = forms.BooleanField(
        label='مرا به خاطر بسپار',
        required=False,
        initial=True,  # فعال کردن پیش‌فرض
        widget=forms.widgets.CheckboxInput(attrs={'class': 'checkbox-inline'}),
        help_text=" با فعال کردن این گزینه، شما با بستن مرورگر از سایت خارج نمی شوید.",
    )


class MobileInputForm(forms.Form):
    mobile_number = forms.CharField(max_length=15,
                                    label=' شماره تلفن همراه',
                                    widget=forms.TextInput(
                                        attrs={'class': "form-control text-center",
                                               'id': "mobile"}),
                                    validators=[
                                        RegexValidator(regex='^0\d{10}$', message='شماره همراه معتبر نیست.'),
                                        validators.MaxLengthValidator(15),
                                    ])


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
