from django import forms
from django.forms import ModelForm


class QuestionForm(forms.Form):
    choices = forms.ChoiceField(label='گزینه درست را انتخاب کنید',
                                widget=forms.RadioSelect,
                                choices=(('0', 'Not at All'),
                                         ('1', 'Sometimes'),
                                         ('2', 'Often'),
                                         ('3', 'Always'))
                                )


