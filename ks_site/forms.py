from captcha.fields import CaptchaField
from django import forms

from ks_site.models import ContactUs
from django.core import validators
from django.core.exceptions import ValidationError


class ContactUsModelForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ['full_name', 'title', 'message', 'user']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control simple'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control simple'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control simple',
                'rows': 5,
                'id': 'message'
            }),
            'user': forms.TextInput(attrs={
                'class': 'form-control simple'
            })
        }

        labels = {
            'full_name': 'نام و نام خانوادگی شما',
            'title': 'موضوع',
            'message': 'متن پیام شما'
        }

        error_messages = {
            'full_name': {
                'required': 'نام و نام خانوادگی اجباری می باشد. لطفا وارد کنید'
            }
        }


class ContactUsForm(forms.Form):
    captcha_field = CaptchaField(
        label='حاصل عبارت رو به رو را وارد کنید',

    )
    mobile = forms.CharField(
        # label='شماره تلفن همراه',
        widget=forms.TextInput(
            attrs={'class': "form-control text-center ",
                   'id': "mobile",
                   'hidden': ""}),
        validators=[
            validators.MaxLengthValidator(11),
        ]
    )
    title = forms.CharField(
        label='موضوع پیام',
        widget=forms.TextInput(
            attrs={'class': "form-control simple",
                   'id': "title"}
        ),
        validators=[
            validators.MaxLengthValidator(20),
        ]
    )
    message = forms.CharField(
        label='متن پیام',
        widget=forms.Textarea(
            attrs={'class': "form-control simple",
                   'rows': 5,
                   'id': "message"}
        ),
        validators=[
            validators.MaxLengthValidator(20),
        ]
    )
