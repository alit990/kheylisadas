from django.urls import path

from ks_subscription.views import PlansList, PlanDetailView, request_payment, verify_payment, plan_free_gift, \
    cancel_pending_payments, try_pay_sms, CampaignDetailView, request_campaign_payment, verify_campaign_payment, \
    CampaignQuestionDetailView

urlpatterns = [
    path('plans', PlansList.as_view(), name='plans_list'),
    # path('plans/<int:pk>/<slug:slug>', PlanDetailView.as_view(), name='plan_detail'),
    path('plans/<int:pk>/<slug:slug>', PlanDetailView.as_view(), name='plan_detail'),
    path('request-payment/<int:plan_id>/<str:code>', request_payment, name='request_payment'),
    path('plan-free-gift/<int:plan_id>/<str:code>', plan_free_gift, name='plan_free_gift'),
    path('verify-payment/', verify_payment, name='verify_payment'),
    path('cancel-pending-payments/', cancel_pending_payments, name='cancel_pending_payments'),

    path('campaign/<int:pk>/<slug:slug>', CampaignDetailView.as_view(), name='campaign_detail'),
    path('campaign-question/<int:campaign_id>/<int:campaign_week_id>', CampaignQuestionDetailView.as_view(),
         name='campaign_question_detail'),
    path('request-campaign-payment/<int:campaign_id>/<int:category_id>/', request_campaign_payment,
         name='request_campaign_payment'),
    path('verify-campaign-payment/', verify_campaign_payment, name='verify_campaign_payment'),
    #  -------------- admin views urls ----------------
    path('payment/<int:payment_id>/try_pay_sms/', try_pay_sms, name='try_pay_sms'),
]
