from unicodedata import name
from django.urls import path
from .views import (
        RegisterView, 
        VerifyUserEmail,
        LoginUserView, 
        TestingAuthenticatedReq, 
        PasswordResetConfirm, 
        PasswordResetRequestView,
        SetNewPasswordView, LogoutApiView, 
        delete_user, ProfileView, UserListView, UserFilterListView,
        VerifyOTPView, ResendOtpView, UpdateUserView, DeleteUserView)

from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('gettoken/', TokenObtainPairView.as_view(), name='gettoken'),
    path('login/', LoginUserView.as_view(), name='login-user'),
    path('verify-email/', VerifyUserEmail.as_view(), name='verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('get-something/', TestingAuthenticatedReq.as_view(), name='just-for-testing'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='reset-password-confirm'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOtpView.as_view(), name='resend-otp'),
    path('set-new-password/', SetNewPasswordView.as_view(), name='set-new-password'),
    path('logout/', LogoutApiView.as_view(), name='logout'),
    path('delete-user/<int:user_id>/', delete_user, name='delete_user'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('update_user/<int:pk>/', UpdateUserView.as_view(), name='user-update'),
    path('delete_user/<int:user_id>/', DeleteUserView.as_view(), name='delete_user'),
    path('userListFilter/', UserFilterListView.as_view(), name='UserFilterListView'),

]
