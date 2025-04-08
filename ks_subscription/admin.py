from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from ks_subscription.models import Plan, Payment, Transaction, GiftPlan, Campaign, Chart, CTransaction, CampaignWeek, \
    CampaignQuestion
from utility.choices import PaymentStatus


class PlanAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'price', 'duration', "is_active"]

    class Meta:
        model = Plan


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'price', 'ref_code', 'is_paid', 'payment_date', 'create_date', 'type', 'status', 'error', 'send_sms_link'] # Include 'error' in list_display

    def send_sms_link(self, obj):
        if obj.status != PaymentStatus.PAID_NO_ERRORS:
            return format_html('<a href="{}">ارسال پیامک</a>', reverse('try_pay_sms', args=[obj.id]))  # بدون namespace
        return ""
    send_sms_link.short_description = 'ارسال پیامک'

    class Meta:
        model = Payment


class TransactionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'payment', 'start_date', 'end_date', 'is_paid', 'in_process']

    class Meta:
        model = Transaction
class CTransactionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'payment', 'start_date', 'end_date', 'is_paid', 'category', 'in_process']

    class Meta:
        model = Transaction

class GiftPlanAdmin(admin.ModelAdmin):
    list_display = ['code', 'percentage', 'max', 'plan', 'is_active', 'is_expired', 'start_date', 'end_date']

    class Meta:
        model = GiftPlan


admin.site.register(Plan, PlanAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(GiftPlan, GiftPlanAdmin)

admin.site.register(Campaign)
admin.site.register(CampaignWeek)
admin.site.register(CampaignQuestion)
admin.site.register(Chart)
admin.site.register(CTransaction, CTransactionAdmin)
