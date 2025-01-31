from django.urls import path

from ks_subscription.views import PlansList, PlanDetailView, request_payment, verify_payment, plan_free_gift, \
    cancel_pending_payments

urlpatterns = [
    path('plans', PlansList.as_view(), name='plans_list'),
    # path('plans/<int:pk>/<slug:slug>', PlanDetailView.as_view(), name='plan_detail'),
    path('plans/<int:pk>/<slug:slug>', PlanDetailView.as_view(), name='plan_detail'),
    path('request-payment/<int:plan_id>/<str:code>', request_payment, name='request_payment'),
    path('plan-free-gift/<int:plan_id>/<str:code>', plan_free_gift, name='plan_free_gift'),
    path('verify-payment/', verify_payment, name='verify_payment'),
    path('cancel-pending-payments/', cancel_pending_payments, name='cancel_pending_payments'),
]
