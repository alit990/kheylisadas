from django.shortcuts import redirect
from django.urls import reverse

def signup_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('mobile_register_view'))  # یا 'users:signup' اگر از namespace استفاده می‌کنید
        return view_func(request, *args, **kwargs)
    return _wrapped_view