from django.contrib import admin

from ks_subscription.models import Plan, Payment, Transaction, GiftPlan


class PlanAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'price', 'duration', "is_active"]

    class Meta:
        model = Plan


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'price', 'ref_code', 'is_paid', 'payment_date', 'create_date', 'type']

    class Meta:
        model = Payment


class TransactionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'payment', 'start_date', 'end_date', 'is_paid', 'in_process']

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
