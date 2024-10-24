from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import os
from subgrantees.models import SubgranteeProfile


from django.db import models


class LDAPUser(models.Model):
    username = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True)
    last_sync = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"LDAP User: {self.username}"


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_approved", True)
        extra_fields.setdefault("organisation_name", "Baylor Uganda")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("email address", unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(null=True, blank=True)
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    organisation_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    subgranteeprofile = models.OneToOneField(
        SubgranteeProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='user_profile'
    )
    is_ldap_user = models.BooleanField(default=False)
    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    # def get_group_permissions(self, obj=None):
    #     permissions = super().get_group_permissions(obj)
    #     if self.ldap_user is not None:  # Check if ldap_user is not None
    #         try:
    #             ldap_permissions = self.ldap_user.get_group_permissions(
    #                 obj)  # Pass obj to get_group_permissions if needed
    #             permissions.update(ldap_permissions)
    #         except AttributeError:
    #             # Log this error or handle it as appropriate for your application
    #             pass
    #     return permissions

    # def get_all_permissions(self, obj=None):
    #     permissions = super().get_all_permissions(obj)
    #     if self.ldap_user is not None:  # Check if ldap_user is not None
    #         try:
    #             ldap_permissions = self.ldap_user.get_all_permissions(
    #                 obj)  # Pass obj to get_all_permissions if needed
    #             permissions.update(ldap_permissions)
    #         except AttributeError:
    #             # Log this error or handle it as appropriate for your application
    #             pass
    #     return permissions

    # groups = models.ManyToManyField(
    #     "auth.Group",
    #     verbose_name="groups",
    #     blank=True,
    #     help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
    #     related_name="customuser_groups",
    #     related_query_name="customuser",
    # )
    # user_permissions = models.ManyToManyField(
    #     "auth.Permission",
    #     verbose_name="user permissions",
    #     blank=True,
    #     help_text="Specific permissions for this user.",
    #     related_name="customuser_user_permissions",
    #     related_query_name="customuser",
    # )

    def send_welcome_email(self):
        frontend_base_url = os.environ.get("FRONTEND_BASE_URL")
        send_mail(
            "Welcome to the Platform",
            f"Congratulations! Your registration has been approved. You can now log in using the following link: {frontend_base_url}/login",
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False,
        )

    def send_pending_approval_email(self):
        send_mail(
            "Registration Pending Approval",
            "Thank you for signing up. Your registration is pending approval. You will receive an email once your registration is approved.",
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False,
        )

    def send_decline_email(self):
        send_mail(
            "Registration Declined",
            "We regret to inform you that your registration has been declined. Please contact the administrator for further information.",
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False,
        )

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)


class Activation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    activation_token = models.CharField(max_length=255)


class PasswordReset(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reset_token = models.CharField(max_length=255)
