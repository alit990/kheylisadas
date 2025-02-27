from django.urls import path, re_path

from ks_account.views import LoginView, LogoutView, MobileRegisterView, ActivationView, UsernameView, ForgetPassMobileView, \
    ForgetPassActivationView

urlpatterns = [
    # path('register-mobile', register_mobile_page, name='register_mobile_page'),  # USED register_mobile_page.html
    # path('forget-password', forget_password_page, name='forget_password_page'),  # USED forget_password_page.html
    # path('confirm-user-code', confirm_user_code, name='confirm_user_code'),  # USED
    # path('confirm-reset-pass-code', confirm_reset_pass_code, name='confirm_reset-pass_code'),  # USED
    # path('register-user', RegisterUserView.as_view(), name='register_user'),  # USED register.html
    #
    # path('pass-changed/login/', PassChangedLoginView.as_view(), name='pass_changed_login_page'),  # USED login.html
    #
    # # from jquery
    # path('send-code', send_code, name='send_code'),  # USED
    # path('send-reset-pass-code', send_reset_pass_code, name='send_reset_pass_code'),  # USED

    path('mobile_register/', MobileRegisterView.as_view(), name='mobile_register_view'),
    path('activation/', ActivationView.as_view(), name='activation_view'),
    path('username/', UsernameView.as_view(), name='username_view'),
    path('forget_pass/', ForgetPassMobileView.as_view(), name='forget_pass_view'),
    path('forget_pass_activation/', ForgetPassActivationView.as_view(), name='forget_pass_activation_view'),

    path('login/', LoginView.as_view(), name='login_page'),  # USED login.html
    path('logout/', LogoutView.as_view(), name='logout_page'),  # USED
]
