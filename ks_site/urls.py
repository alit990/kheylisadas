from django.urls import path

from ks_site.views import ContactUsView, FrequentQuestionList, AboutUsView

urlpatterns = [
    path('contact-us', ContactUsView.as_view(), name='contact_us'),
    path('about-us', AboutUsView.as_view(), name='about_us'),
    path('frequent-questions', FrequentQuestionList.as_view(), name='frequent_questions'),
]
