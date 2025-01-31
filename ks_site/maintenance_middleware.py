# maintenance_middleware.py
from django.shortcuts import render
from .models import SiteSetting


class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # بررسی استثناءهای مسیر پنل ادمین و صفحه به‌روزرسانی
        if not request.path.startswith('/ks-admin-panel/') and not request.path.startswith(
                '/maintenance/') and not request.user.is_staff:
            try:
                site_setting = SiteSetting.objects.filter(is_main_setting=True).first()
                if site_setting and site_setting.maintenance_mode:
                    return render(request, 'maintenance.html')
            except SiteSetting.DoesNotExist:
                pass

        response = self.get_response(request)
        return response
