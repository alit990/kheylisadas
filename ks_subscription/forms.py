from captcha.fields import CaptchaField
from django import forms
from django.core import validators
from django import forms

from ks_category.models import Category

class CampaignQuestionForm(forms.Form):
    captcha_field = CaptchaField(
        label='حاصل عبارت رو به رو را وارد کنید',
    )
    mobile = forms.CharField(
        widget=forms.HiddenInput(),  # فیلد مخفی
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
    )
    message = forms.CharField(
        label='متن پیام',
        widget=forms.Textarea(
            attrs={'class': "form-control simple",
                   'rows': 5,
                   'id': "message"}
        ),
    )
class CategoryChoiceForm(forms.Form):
    category = forms.ChoiceField(
        choices=[],
        widget=forms.RadioSelect,
        label='لطفا حتما سن کودک خود را انتخاب کنید:',
    )

    def __init__(self, *args, **kwargs):
        categories = kwargs.pop('categories', None)
        super().__init__(*args, **kwargs)
        if categories:
            self.fields['category'].choices = [(category.id, category.age_range) for category in categories]
            self.fields['category'].label_suffix = ""
            if categories:
                self.fields['category'].initial = categories[0].id


class GiftCodeForm(forms.Form):
    code = forms.CharField(
        label='کد تخفیف',
        widget=forms.TextInput(
            attrs={'class': "form-control simple text-center flex_cart_1",
                   'id': "code"}
        ),
        validators=[
            validators.MaxLengthValidator(10),
        ]
    )

# class GiftCodeForm(forms.Form):
#
#     code = forms.CharField(
#         label='کد تخفیف',
#         widget=forms.TextInput(
#             attrs={'class': "form-control simple flex_cart_1",
#                    'id': "code"}
#         ),
#         error_messages={
#             'invalid': 'کد تخفیف نامعتبر است.'
#         },
#         validators=[
#             validators.MaxLengthValidator(10),
#         ]
#     )
#
#     def __init__(self, *args, **kwargs):
#         super(GiftCodeForm, self).__init__(*args, **kwargs)
#         for field in self.fields.values():
#             field.error_messages = {'invalid': 'کد تخفیف نامعتبر است.'}
#             field.widget.attrs.update({'class': 'form-control text-danger'})
