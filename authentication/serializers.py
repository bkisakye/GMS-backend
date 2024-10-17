from rest_framework import serializers
from .models import CustomUser


class AuthSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)


class GranteeSignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    fname = serializers.CharField(max_length=30)
    lname = serializers.CharField(max_length=30)
    password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)
    organisation_name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=15)


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = fields = ('id', 'is_staff', 'fname', 'lname', 'email', 'organisation_name',
                           'phone_number', 'is_approved')
