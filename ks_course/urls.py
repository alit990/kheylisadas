from django.urls import path
from . import views
from .views import CoursesListView, CourseDetailView, add_course_comment, CoursePriceDetailView, \
    course_request_payment, \
    course_verify_payment, course_free_gift

urlpatterns = [
    path('', CoursesListView.as_view(), name='courses_list'),
    path('<int:pk>/<slug:slug>', CourseDetailView.as_view(), name='course_detail'),
    path('add-course-comment', add_course_comment, name='add_course_comment'),

    path('course-price/<int:pk>/<slug:slug>', CoursePriceDetailView.as_view(), name='course_price_detail'),
    path('course-free-gift/<int:course_id>/<str:code>', course_free_gift, name='course_free_gift'),
    path('course-request-payment/<int:course_id>/<str:code>', course_request_payment, name='course_request_payment'),
    path('course-verify-payment/', course_verify_payment, name='course_verify_payment')

]
