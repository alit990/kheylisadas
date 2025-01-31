from django.urls import path
from ks_user_panel.views import UserPanelDashboardPage, EditUserProfilePage, ChangePasswordPage, \
    user_panel_playlist_page, PaymentsPage, ContactsPage

urlpatterns = [
    path('', UserPanelDashboardPage.as_view(), name='user_panel_dashboard'),
    path('user-payments', PaymentsPage.as_view(), name='user_payments'),
    path('user-contacts', ContactsPage.as_view(), name='user_contacts'),
    # path('edit-profile', EditUserProfilePage.as_view(), name='edit_profile_page'),
    # tadakhol upload file and sorl
    # form not valid | date | ...
    path('change-pass', ChangePasswordPage.as_view(), name='change_password_page'),
    path('user-playlist', user_panel_playlist_page, name='user_panel_playlist_page'),

]
