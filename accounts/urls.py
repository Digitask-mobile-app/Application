from unicodedata import name
from django.urls import path
from . import views

from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('gettoken/', TokenObtainPairView.as_view(), name='gettoken'),
    path('login/', views.LoginUserView.as_view(), name='login-user'),
    path('verify-email/', views.VerifyUserEmail.as_view(), name='verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('get-something/', views.TestingAuthenticatedReq.as_view(),
         name='just-for-testing'),
    path('password-reset/', views.PasswordResetRequestView.as_view(),
         name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         views.PasswordResetConfirm.as_view(), name='reset-password-confirm'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify-otp'),
    path('resend-otp/', views.ResendOtpView.as_view(), name='resend-otp'),
    path('set-new-password/', views.SetNewPasswordView.as_view(),
         name='set-new-password'),
    path('logout/', views.LogoutApiView.as_view(), name='logout'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('profile/', views.ProfileRetrieveView.as_view(), name='profile-retrieve'),
    path('profile_update/', views.ProfileView.as_view(), name='profile-update'),
    path('profile_image_update/', views.ProfileImageUpdateView.as_view(), name='profile-image-update'),
    
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('update_user/<int:pk>/', views.UpdateUserView.as_view(), name='user-update'),
    path('delete_user/<int:user_id>/',
         views.DeleteUserView.as_view(), name='delete_user'),
    path('userListFilter/', views.UserFilterListView.as_view(),
         name='UserFilterListView'),
    path('add_group/', views.AddGroup.as_view(), name='AddGroup'),
    path('rooms/<int:id>/add-members/',
         views.AddMembersView.as_view(), name='add-members'),
    path('rooms/<int:id>/remove-members/',
         views.RemoveMembersView.as_view(), name='remove-members'),
    path('messages/', views.MessageListView.as_view(), name='message-list'),
    path('messages_mobile/', views.MessagesListView.as_view(), name='message-list_mobile'),
    
    path('RoomsApiView/', views.RoomsApiView.as_view(), name='RoomsApiView'),
    path('reportsListView/', views.NotificationListView.as_view(), name='NotificationListView'),
    path('notifications/mark-as-read/', views.MarkNotificationsAsReadView.as_view(),
         name='mark-notifications-as-read'),
]
