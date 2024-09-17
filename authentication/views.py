from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from notifications.models import Notification
from .serializers import AuthSerializer, LoginSerializer, GranteeSignupSerializer, CustomUserSerializer
from .models import CustomUser
import logging
from subgrantees.models import SubgranteeProfile
from rest_framework.decorators import api_view
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes

logger = logging.getLogger(__name__)


class AuthenticateUser(APIView):
    """
    API endpoint for authenticating users with username and password.
    """

    def post(self, request, *args, **kwargs):
        serializer = AuthSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            user = authenticate(request, username=username, password=password)

            if user is not None:
                return Response(
                    {"message": "User authenticated",
                        "username": user.get_username()},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUserView(APIView):
    """
    API endpoint for logging in users using email and password.
    """

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            user = authenticate(request, email=email, password=password)

            if user:
                if user.is_active and user.is_staff:
                    # Admin login
                    refresh = RefreshToken.for_user(user)
                    return Response(
                        {
                            "organisation_name": user.organisation_name,
                            "user_id": user.id,  
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        },
                        status=status.HTTP_200_OK,
                    )
                elif user.is_active and hasattr(user, 'is_approved') and user.is_approved:
                    # Grantee login
                    refresh = RefreshToken.for_user(user)
                    return Response(
                        {
                            "organisation_name": user.organisation_name,
                            "user_id": user.id,  # Include user ID
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        },
                        status=status.HTTP_200_OK,
                    )
            return Response(
                {"error": "Invalid credentials or account not activated/approved."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GranteeSignupView(APIView):
    """
    API endpoint for grantee sign-up.
    """

    def post(self, request, *args, **kwargs):
        serializer = GranteeSignupSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]

            # Check if the email already exists
            if CustomUser.objects.filter(email=email).exists():
                return Response(
                    {"error": "Email already in use."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            fname = serializer.validated_data["fname"]
            lname = serializer.validated_data["lname"]
            password = serializer.validated_data["password"]
            organisation_name = serializer.validated_data["organisation_name"]
            phone_number = serializer.validated_data["phone_number"]

            # Create a new CustomUser instance with is_approved set to False
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                fname=fname,
                lname=lname,
                organisation_name=organisation_name,
                phone_number=phone_number,
                is_approved=None,
            )

            # Send an email to the grantee
            user.send_pending_approval_email()

            # Notify the admin
            SubgranteeProfile.objects.create(user=user)
            # self.notify_admin(user)

            return Response(
                {"message": "Signup request received. Please wait for admin approval."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_subgrantees_count(request):
    subgrantees_count = CustomUser.objects.filter(is_staff=False).count()
    return Response({"count": subgrantees_count})

@api_view(['GET'])
def get_active_subgrantees_count(request):
    active_subgrantees_count = CustomUser.objects.filter(is_staff=False, is_approved=True).count()
    return Response({"count": active_subgrantees_count})

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def get_all_subgrantees(request):
    subgrantees = CustomUser.objects.filter(is_staff=False)
    serializer = CustomUserSerializer(subgrantees, many=True)
    return Response(serializer.data) 

class AdminApprovalView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        approve = request.data.get("approve")

        if not email:
            return Response(
                {"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Grantee not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if approve:
            user.is_approved = True
            user.save()
            user.send_welcome_email()
            return Response(
                {"message": "Grantee approved and notified."}, status=status.HTTP_200_OK
            )
        else:
            # Optionally, handle rejection
            send_mail(
                "Registration Rejected",
                "We regret to inform you that your registration has been rejected.",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

        return Response(
            {"message": "Grantee status updated."}, status=status.HTTP_200_OK
        )

@api_view(['DELETE'])
@permission_classes([permissions.IsAdminUser])
def delete_subgrantee(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        user.delete()
        return Response({"message": "Subgrantee deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except CustomUser.DoesNotExist:
        return Response({"error": "Subgrantee not found."}, status=status.HTTP_404_NOT_FOUND)