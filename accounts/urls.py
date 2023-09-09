from django.urls import path
from django.contrib.auth import views as auth_views

from accounts import views

app_name = "accounts"

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
	path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('email_sent/', views.email_sent_view, name='email_sent'),
    path('user-account/', views.user_account_view, name="user_account"),
    path('change-password/', views.change_password_view, name="change_password"),
    path('logout/', views.logout_view, name='logout'),
]