from django import forms
from .models import AudioChapter


class AudioChapterForm(forms.ModelForm):
    class Meta:
        model = AudioChapter
        fields = ['name', 'start_time', 'is_active', 'is_delete']
