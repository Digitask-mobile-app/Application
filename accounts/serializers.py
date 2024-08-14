from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from .models import User, OneTimePassword, Group
from services.serializers import GroupSerializer
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from rest_framework.authtoken.models import Token
from datetime import timedelta


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    password2 = serializers.CharField(
        max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'group',
                  "user_type", 'username', 'password', 'password2', 'phone']

    def validate(self, attrs):
        password = attrs.get('password', '')
        password2 = attrs.get('password2', '')
        if password != password2:
            raise serializers.ValidationError("Parollar uyğun gəlmir")

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            password=validated_data.get('password'),
            group=validated_data.get('group'),
            username=validated_data.get('username'),
            user_type=validated_data.get('user_type'),
            phone=validated_data.get('phone'),
        )
        return user


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=155, min_length=6)
    password = serializers.CharField(max_length=68, write_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)
    remember_me = serializers.BooleanField(default=False, write_only=True)
    user_type = serializers.CharField(max_length=20, read_only=True)
    is_admin = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'access_token',
                  'refresh_token', 'user_type', 'is_admin', 'remember_me']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        remember_me = attrs.get('remember_me')
        request = self.context.get('request')
        user = authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed(
                "Etibarsız etimadnamələr, yenidən cəhd edin.")

        tokens = user.tokens()
        refresh = RefreshToken.for_user(user)

        if remember_me:
            refresh.set_exp(lifetime=timedelta(days=30))

        access_token = refresh.access_token
        if remember_me:
            access_token.set_exp(lifetime=timedelta(days=30))

        is_admin = False
        if user.user_type == 'Ofis menecer' or user.user_type == 'Texnik menecer':
            is_admin = True

        is_admin = False
        if user.user_type == 'Ofis menecer' or user.user_type == 'Texnik menecer':
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
            raise ValidationError(
                "Bu e-poçt ünvanı ilə qeydiyyatdan keçilməyib.")

        user = User.objects.get(email=email)

        OneTimePassword.objects.filter(user=user).delete()

        otp = get_random_string(length=4, allowed_chars='0123456789')
        OneTimePassword.objects.create(user=user, otp=otp)

        email_body = f"Salam {user.first_name}, parolunuzu sıfırlamaq üçün aşağıdakı OTP kodunu istifadə edin: {otp}"
        data = {
            'email_body': email_body,
            'email_subject': "Şifrəni sıfırlamaq üçün OTP kodu",
            'to_email': user.email
        }
        send_mail(
            data['email_subject'],
            data['email_body'],
            'no-reply@yourdomain.com',
            [data['to_email']],
            fail_silently=False,
        )

        return super().validate(attrs)


class VerifyOTPSerializer(serializers.Serializer):
    otp = serializers.CharField()

    def validate(self, data):
        otp = data['otp']
        try:
            otp_record = OneTimePassword.objects.get(otp=otp)
            user = otp_record.user
            data['user'] = user
        except OneTimePassword.DoesNotExist:
            raise serializers.ValidationError('Invalid OTP.')

        token, created = Token.objects.get_or_create(user=user)
        data['token'] = token.key
        otp_record.delete()

        return data


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=100, min_length=6, write_only=True)
    confirm_password = serializers.CharField(
        max_length=100, min_length=6, write_only=True)
    token = serializers.CharField(write_only=True)

    def validate(self, attrs):
        token = attrs.get('token')
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError("Parollar uyğun gəlmir")

        try:
            user = Token.objects.get(key=token).user
        except Token.DoesNotExist:
            raise serializers.ValidationError(
                "Etibarsız və ya vaxtı keçmiş nişan")

        attrs['user'] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user']
        password = self.validated_data['password']

        user.set_password(password)
        user.save()

        Token.objects.filter(user=user).delete()

        return user


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
    otp = serializers.CharField(max_length=4)


class ProfileSerializer(serializers.ModelSerializer):
    groupData = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), required=False)
    group = GroupSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone',
            'user_type', 'groupData', 'group'
        ]

    def update(self, instance, validated_data):
        group_data = validated_data.pop('groupData', None)
        if group_data:
            instance.group = Group.objects.get(id=group_data.id)
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.user_type = validated_data.get(
            'user_type', instance.user_type)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    group = GroupSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name',
                  'phone', 'user_type', 'group', 'username']


class UserFilterSerializer(serializers.ModelSerializer):
    group = GroupSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name',
                  'last_name',  'user_type', 'group']


class UpdateUserSerializer(serializers.ModelSerializer):
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), write_only=True, required=False, allow_null=True)
    password = serializers.CharField(
        write_only=True, required=False, allow_blank=True, allow_null=True)
    password2 = serializers.CharField(
        write_only=True, required=False, allow_blank=True, allow_null=True)
    group = GroupSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone', 'user_type', 'username',
            'group', 'group_id', 'password', 'password2',
            'first_name', 'last_name'
        ]
        extra_kwargs = {
            'email': {'required': False},
            'phone': {'required': False, 'allow_blank': True, 'allow_null': True},
            'user_type': {'required': False, 'allow_blank': True, 'allow_null': True},
            'username': {'required': False, 'allow_blank': True, 'allow_null': True},
            'group_id': {'required': False, 'allow_null': True},
            'password': {'required': False},
            'password2': {'required': False},
            'first_name': {'read_only': True},
            'last_name': {'read_only': True},
            'group': {'read_only': True},
        }

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')

        if (password or password2) and not password:
            raise serializers.ValidationError(
                {"password": "Bu sahə təkrar şifrə təmin edildikdə tələb olunur."})
        if (password or password2) and not password2:
            raise serializers.ValidationError(
                {"password2": "Şifrə təmin edildikdə bu sahə tələb olunur."})
        if password and password2 and password != password2:
            raise serializers.ValidationError(
                {"password2": "İki şifrə sahəsi eyni olmalıdır."})

        return data

    def update(self, instance, validated_data):
        group = validated_data.pop('group_id', None)
        if group is not None:
            instance.group = group
        else:
            instance.group = None
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def get_groupName(self, obj):
        return obj.group.group if obj.group else None

    def get_groupRegion(self, obj):
        return obj.group.region if obj.group else None


class PerformanceUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'user_type']
