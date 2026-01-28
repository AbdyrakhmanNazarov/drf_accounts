from django.urls import path
from .views import (
    RegistrationView, LoginView, LogoutView, ProfileView,
    SendOTPView, ChangePasswordView, ForgotPasswordView, ResetPasswordView
)

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('send-code/', SendOTPView.as_view(), name='send_code'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
]
