from ast import Expression
from multiprocessing import context
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .models import OneTimePassword, User
from .serializers import *
from rest_framework import status, generics, permissions, viewsets
from .utils import send_generated_otp_to_email
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.views import APIView
from .serializers import UserSerializer
from .filters import UserFilter,UserTypeFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.db.models import Q 

from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.db import IntegrityError



class RegisterView(GenericAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [IsAdminUser]

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        if serializer.is_valid(raise_exception=True):
            user_instance = serializer.save()
            user_data = serializer.data
            if not user_instance.is_verified:
                return Response({
                    'data': user_data,
                    'message': 'User registered successfully'
                }, status=status.HTTP_201_CREATED)
            return Response({
                'data': user_data,
                'message': 'User registered but email verification is pending'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class VerifyUserEmail(GenericAPIView):
    serializer_class = VerifyUserEmailSerializer
    def post(self, request):
        try:
            passcode = request.data.get('otp')
            user_pass_obj=OneTimePassword.objects.get(otp=passcode)
            user=user_pass_obj.user
            if not user.is_verified:
                user.is_verified=True
                user.save()
                return Response({
                    'message':'account email verified successfully'
                }, status=status.HTTP_200_OK)
            return Response({'message':'passcode is invalid user is already verified'}, status=status.HTTP_204_NO_CONTENT)
        except OneTimePassword.DoesNotExist as identifier:
            return Response({'message':'passcode not provided'}, status=status.HTTP_400_BAD_REQUEST)
        

class LoginUserView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data.get('email') 
        
        return Response({'message': 'OTP kodunu e-poçtunuza göndərdik.', 'email': email}, status=status.HTTP_200_OK)

    
class PasswordResetConfirm(GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'message': 'Token etibarsızdır və ya vaxtı keçib'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success': True, 'message': 'Etibarnamələr etibarlıdır', 'uidb64': uidb64, 'token': token}, status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError as identifier:
            return Response({'message': 'Token etibarsızdır və ya vaxtı keçib'}, status=status.HTTP_401_UNAUTHORIZED)


class VerifyOTPView(GenericAPIView):
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response({'token': serializer.validated_data['token']}, status=status.HTTP_200_OK)

class ResendOtpView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data.get('email')
        
        return Response({'message': 'Yeni OTP kodu e-poçtunuza göndərildi.'}, status=status.HTTP_200_OK)

class SetNewPasswordView(GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)


class TestingAuthenticatedReq(GenericAPIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):

        data={
            'msg':'its works'
        }
        return Response(data, status=status.HTTP_200_OK)

class LogoutApiView(GenericAPIView):
    serializer_class=LogoutUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
 
def delete_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if hasattr(user, 'onetimepassword'):
        user.onetimepassword.delete()
    user.delete()
    return HttpResponse("User and related OneTimePassword deleted successfully")


from django.db import connection


def delete_task(task_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM myapp_task WHERE id = %s", [task_id])

def update_auto_increment():
    with connection.cursor() as cursor:
        cursor.execute("UPDATE sqlite_sequence SET seq = (SELECT MAX(id) FROM myapp_task) WHERE name = 'myapp_task'")

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = UserFilter
    search_fields = ['first_name', 'last_name']

    def get_queryset(self):
        queryset = User.objects.filter(user_type__in=["Texnik", "Plumber", "Ofis menecer", "Texnik menecer"])

        search_term = self.request.query_params.get('search', None)
        if search_term:
            queryset = queryset.filter(
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term)
            )

        return queryset
    
class UpdateUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UpdateUserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return Response({"mesaj": "İstifadəçi uğurla silindi."}, status=status.HTTP_204_NO_CONTENT)
    

class UserFilterListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserFilterSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserTypeFilter