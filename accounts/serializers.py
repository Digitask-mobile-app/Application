import json
from dataclasses import field
from .models import User, Group
from services.serializers import GroupSerializer
from rest_framework import serializers
from string import ascii_lowercase, ascii_uppercase
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import send_normal_email
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.core.exceptions import ValidationError


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2= serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model=User
        fields = ['email', 'first_name', 'last_name', 'group', "user_type", 'username', 'password', 'password2']

    def validate(self, attrs):
        password=attrs.get('password', '')
        password2 =attrs.get('password2', '')
        if password !=password2:
            raise serializers.ValidationError("passwords do not match")
         
        return attrs

    def create(self, validated_data):
        user= User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            password=validated_data.get('password'),
            group=validated_data.get('group'),
            username=validated_data.get('username'),
            user_type=validated_data.get('user_type'),
            )
        return user
    

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=155, min_length=6)
    password = serializers.CharField(max_length=68, write_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)
    user_type = serializers.CharField(max_length=20, read_only=True)
    is_admin = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'access_token', 'refresh_token', 'user_type', 'is_admin']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        request = self.context.get('request')
        user = authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed("Invalid credentials, try again.")

        tokens = user.tokens()
        
        is_admin = False
        if user.user_type == 'office_manager' or user.user_type == 'tech_manager':
            is_admin = True

        return {
            'email': user.email,
            'access_token': str(tokens.get('access')),
            'refresh_token': str(tokens.get('refresh')),
            'user_type': user.user_type,
            'is_admin': is_admin
        }


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError("Bu e-poçt ünvanı ilə qeydiyyatdan keçilməyib.")
        
        user = User.objects.get(email=email)
        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        request = self.context.get('request')
        current_site = get_current_site(request).domain
        relative_link = reverse('reset-password-confirm', kwargs={'uidb64': uidb64, 'token': token})
        abslink = f"http://{current_site}{relative_link}"
        print(abslink)
        email_body = f"Salam {user.first_name}, parolunuzu sıfırlamaq üçün aşağıdakı linkdən istifadə edin: {abslink}"
        data = {
            'email_body': email_body, 
            'email_subject': "Reset your Password", 
            'to_email': user.email
        }
        send_normal_email(data)

        return super().validate(attrs)

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    confirm_password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)
    token = serializers.CharField(min_length=3, write_only=True)

    class Meta:
        fields = ['password', 'confirm_password', 'uidb64', 'token']

    def validate(self, attrs):
        try:
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            password = attrs.get('password')
            confirm_password = attrs.get('confirm_password')

            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("Reset link is invalid or has expired", 401)
            if password != confirm_password:
                raise AuthenticationFailed("Passwords do not match")
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            raise AuthenticationFailed("Link is invalid or has expired")


    
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError

class LogoutUserSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    access_token = serializers.CharField()

    default_error_messages = {
        'bad_token': 'Token is expired or invalid'
    }

    def validate(self, attrs):
        self.refresh_token = attrs.get('refresh_token')
        self.access_token = attrs.get('access_token')
        return attrs

    def save(self, **kwargs):
        try:
            refresh_token = RefreshToken(self.refresh_token)
            refresh_token.blacklist()
            
            access_token = AccessToken(self.access_token)
            access_token.blacklist()

        except TokenError:
            self.fail('bad_token')



class VerifyUserEmailSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)

class ProfileSerializer(serializers.ModelSerializer):
    group = GroupSerializer()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone',
            'user_type', 'group',
        ]

class UserSerializer(serializers.ModelSerializer):
    group = GroupSerializer()
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'user_type', 'group','is_staff']

class PerformanceUserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = ['id', 'first_name', 'last_name', 'user_type']