from captcha.fields import CaptchaField
from django import forms
from django.core import validators


class LoginForm(forms.Form):
    # captcha = ReCaptchaField(
    #     label='امنیت',
    #     widget=ReCaptchaV2Checkbox(api_params={
    #         'hl': 'fa'
    #     }),
    # error_messages='احراز هویت تایید نشد'
    # )
    captcha_field = CaptchaField(
        label='حاصل عبارت رو به رو را وارد کنید',

    )
    username = forms.CharField(
        label='نام کاربری',
        # label='username',
        widget=forms.TextInput(
            attrs={'class': "form-control text-center",
                   'id': "username"}
        ),
        validators=[
            validators.MaxLengthValidator(20),
            # validators.EmailValidator,
        ]
    )
    password = forms.CharField(
        label='کلمه عبور',
        # label='password',
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
        # disabled=True,
        widget=forms.widgets.CheckboxInput(attrs={'class': 'checkbox-inline'}),
        help_text=" با فعال کردن این گزینه، شما با بستن مرورگر از سایت خارج نمی شوید.",
        # error_messages={'required': 'Please check the box'}
    )




class MobileInputForm(forms.Form):
    mobile_number = forms.CharField(max_length=15,
                                    label=' شماره تلفن همراه',
                                    widget=forms.TextInput(
                                       attrs={'class': "form-control text-center",
                                              'id': "mobile"}),
                                    validators=[
                                       validators.MaxLengthValidator(15),
                                   ])


class ActivationForm(forms.Form):
    activation_code = forms.CharField(max_length=4,
                                      label=' کد فعالسازی',
                                      widget=forms.TextInput(
                                          attrs={'class': "form-control text-center",
                                                 'id': "activation_code"}),
                                      validators=[
                                          validators.MaxLengthValidator(6),
                                      ]
                                      )


class UsernameForm(forms.Form):
    username = forms.CharField(max_length=30,
                               label=' نام کاربری',
                               widget=forms.TextInput(
                                   attrs={'class': "form-control text-center",
                                          'id': "username"}),
                               validators=[
                                   validators.MinLengthValidator(5),
                               ]
                               )
