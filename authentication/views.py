from django_auth_ldap.backend import LDAPBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from notifications.models import Notification
from .serializers import AuthSerializer, LoginSerializer, GranteeSignupSerializer, CustomUserSerializer
import logging
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes

logger = logging.getLogger(__name__)
CustomUser = get_user_model()


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

            if user:
                logger.info(f"User {username} authenticated successfully.")
                return Response(
                    {"message": "User authenticated",
                        "username": user.get_username()},
                    status=status.HTTP_200_OK,
                )
            logger.warning(
                f"Failed login attempt for user: {username}. Invalid credentials.")
            return Response(
                {"message": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUserView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            # Extract username from email for LDAP authentication
            username = email.split('@')[0]

            # Try LDAP authentication first
            user = authenticate(request, username=username, password=password)

            if user is None:
                # If LDAP fails, try local authentication
                user = authenticate(request, email=email, password=password)

            if user:
                # Log user data after authentication
                logger.debug(
                    f"Authenticated user: {user.email}, fname: {user.fname}, lname: {user.lname}, is_ldap_user: {user.is_ldap_user}")

                if user.is_active:
                    # Check if user is approved (for subgrantees)
                    if hasattr(user, 'is_approved') and not user.is_approved:
                        logger.warning(
                            f"Unapproved user tried to log in: {email}.")
                        return Response({"error": "Account not approved yet."}, status=status.HTTP_401_UNAUTHORIZED)

                    # Generate JWT tokens
                    refresh = RefreshToken.for_user(user)

                    # Prepare response data
                    response_data = {
                        "user_id": user.id,
                        "email": user.email,
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                        "is_ldap_user": getattr(user, 'is_ldap_user', True),
                        "organisation_name": user.organisation_name if hasattr(user, 'organisation_name') else None,
                    }

                    return Response(response_data, status=status.HTTP_200_OK)

                logger.warning(f"Inactive user tried to log in: {email}.")
                return Response({"error": "Account not activated."}, status=status.HTTP_401_UNAUTHORIZED)

            logger.warning(f"Invalid credentials for email: {email}.")
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

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
                logger.warning(f"Email already in use: {email}.")
                return Response(
                    {"error": "Email already in use."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create a new CustomUser instance with is_approved set to False
            user = CustomUser.objects.create_user(
                email=email,
                password=serializer.validated_data["password"],
                fname=serializer.validated_data["fname"],
                lname=serializer.validated_data["lname"],
                organisation_name=serializer.validated_data["organisation_name"],
                phone_number=serializer.validated_data["phone_number"],
                is_approved=False,
            )

            try:
                user.send_pending_approval_email()
                logger.info(f"Pending approval email sent to: {email}.")
            except Exception as e:
                logger.error(f"Error sending email to {email}: {e}")

            return Response(
                {"message": "Signup request received. Please wait for admin approval."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_subgrantees_count(request):
    count = CustomUser.objects.filter(is_staff=False).count()
    return Response({"count": count})


@api_view(['GET'])
def get_active_subgrantees_count(request):
    count = CustomUser.objects.filter(is_staff=False, is_approved=True).count()
    return Response({"count": count})


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
            user.send_welcome_email()  # Consider catching exceptions here too
            logger.info(f"Grantee approved: {email}.")
            return Response(
                {"message": "Grantee approved and notified."}, status=status.HTTP_200_OK
            )
        else:
            send_mail(
                "Registration Rejected",
                "We regret to inform you that your registration has been rejected.",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            logger.info(f"Grantee rejected: {email}.")

        return Response(
            {"message": "Grantee status updated."}, status=status.HTTP_200_OK
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAdminUser])
def delete_subgrantee(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        user.delete()
        logger.info(f"Subgrantee deleted successfully: {user_id}.")
        return Response({"message": "Subgrantee deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except CustomUser.DoesNotExist:
        logger.error(f"Subgrantee not found: {user_id}.")
        return Response({"error": "Subgrantee not found."}, status=status.HTTP_404_NOT_FOUND)
