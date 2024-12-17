from django import forms
from django.core import validators


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
