from django import forms
from django.core import validators
from django.core.exceptions import ValidationError

from ks_account.models import User


class EditProfileModelForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'avatar', 'gender', 'birthday', 'address', 'about_user']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'gender': forms.RadioSelect(choices=model.GENDER_CHOICES, 
                                        attrs={
                'class': 'form-control',
                'rows': 1,
            }),
            'birthday': forms.DateInput(attrs={
                'class': 'form-control',
                'rows': 1,
                'id': 'birthday',
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'rows': 1,
            }),
            'about_user': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'id': 'message'
            })
        }

        labels = {
            'first_name': 'name',
            'last_name': 'last',
            'avatar': 'avatar',
            'gender': 'gender',
            'birthday': 'birthday',
            'address': 'address',
            'about_user': 'about',
        }
        # labels = {
        #     'first_name': 'نام',
        #     'last_name': 'نام خانوادگی',
        #     'avatar': 'تصویر پروفایل',
        #     'gender': 'جنسیت',
        #     'birthday': 'تاریخ تولد',
        #     'address': 'شهر محل سکونت',
        #     'about_user': 'درباره من',
        # }


class ChangePasswordForm(forms.Form):
    error_css_class = 'alert alert-danger'
    current_password = forms.CharField(
        label='کلمه عبور فعلی',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control form-group col-md-6 text-center'
            }
        ),
        validators=[
            validators.MaxLengthValidator(100),
        ]
    )
    password = forms.CharField(
        label='کلمه عبور جدید',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control form-group col-md-6 text-center'
            }
        ),
        validators=[
            validators.MaxLengthValidator(100),
        ]
    )
    confirm_password = forms.CharField(
        label='تکرار کلمه عبور جدید',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control form-group col-md-6 text-center'
            }
        ),
        validators=[
            validators.MaxLengthValidator(100),
        ]
    )

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password == confirm_password:
            return confirm_password

        raise ValidationError('کلمه عبور و تکرار کلمه عبور مغایرت دارند')
