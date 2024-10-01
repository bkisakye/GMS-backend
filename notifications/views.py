from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notification
from authentication.models import CustomUser
from rest_framework import status
from rest_framework.views import APIView
from .serializers import NotificationSerializer


class NotificationsListView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_permissions(self):
        # Allow superusers unrestricted access
        if self.request.user.is_superuser:
            return []

        # Otherwise, require authentication
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Notification.objects.filter(notification_type='admin')
        else:
            return Notification.objects.filter(user=user, notification_type='grantee')


class CreateNotificationView(APIView):
    def get_permissions(self):
        # Allow superusers unrestricted access
        if self.request.user.is_superuser:
            return []

        # Otherwise, require authentication
        return [IsAuthenticated()]

    def post(self, request, *args, **kwargs):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            # Save the notification and return a success response
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationsCountView(generics.GenericAPIView):
    def get_permissions(self):
        # Allow superusers unrestricted access
        if self.request.user.is_superuser:
            return []

        # Otherwise, require authentication
        return [IsAuthenticated()]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            count = Notification.objects.filter(
                notification_type='admin', is_read=False).count()
        else:
            count = Notification.objects.filter(
                user=user, notification_type='grantee', is_read=False).count()
        return Response({"count": count})


class MarkNotificationAsReadView(APIView):
    def get_permissions(self):
        # Allow superusers unrestricted access
        if self.request.user.is_superuser:
            return []

        # Otherwise, require authentication
        return [IsAuthenticated()]

    def patch(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({"status": "notification marked as read"})
        except Notification.DoesNotExist:
            return Response(
                {"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND
            )


class ApproveNotificationView(APIView):
    def get_permissions(self):
        # Allow superusers unrestricted access
        if self.request.user.is_superuser:
            return []

        # Otherwise, require authentication
        return [IsAuthenticated()]

    def patch(self, request, pk):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email not provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            notification = Notification.objects.get(pk=pk)
            user = CustomUser.objects.get(email=email)
            user.is_approved = True
            user.save()
            user.send_welcome_email()
            notification.status = "approved"
            notification.is_read = True
            notification.save()
            return Response({"status": "approved"}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response(
                {"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class DeclineNotificationView(APIView):
    def get_permissions(self):
        # Allow superusers unrestricted access
        if self.request.user.is_superuser:
            return []

        # Otherwise, require authentication
        return [IsAuthenticated()]

    def patch(self, request, pk):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email not provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            notification = Notification.objects.get(pk=pk)
            user = CustomUser.objects.get(email=email)
            user.is_approved = False
            user.save()
            user.send_decline_email()
            notification.status = "declined"
            notification.is_read = True
            notification.save()
            return Response({"status": "declined"}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response(
                {"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND
            )


class NotificationDetailView(APIView):
    def get_permissions(self):
        # Allow superusers unrestricted access
        if self.request.user.is_superuser:
            return []

        # Otherwise, require authentication
        return [IsAuthenticated()]

    def get(self, request, pk, *args, **kwargs):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            data = {
                "text": notification.text,
                "timestamp": notification.timestamp,
                "is_read": notification.is_read,
                "status": notification.status,
            }

            if notification.notification_category == 'new_grant':
                grant = Grant.objects.get(pk=notification.grant_id)
                data['grant'] = {
                    "name": grant.name,
                    "description": grant.description,
                    "start_date": grant.start_date,
                    "end_date": grant.end_date,
                    "amount": grant.amount,
                }
            elif notification.notification_category == 'grant_application':
                application = GrantApplication.objects.get(
                    pk=notification.application_id)
                data['application'] = {
                    "grant": application.grant.name,
                    "submitted_by": application.subgrantee.user.get_full_name(),
                    "date_submitted": application.date_submitted,
                }
            elif notification.notification_category == 'grant_review':
                review = GrantApplicationReview.objects.get(
                    pk=notification.review_id)
                data['review'] = {
                    "reviewer": review.reviewer.get_full_name(),
                    "date_reviewed": review.date_reviewed,
                    "status": review.status,
                    "comments": review.comments,
                }
            elif notification.notification_category == 'new_subgrantee':
                subgrantee = SubgranteeProfile.objects.get(
                    pk=notification.subgrantee_id)
                data['subgrantee'] = {
                    "organization_name": subgrantee.user.organization_name,
                    "contact_person": subgrantee.contact_person,
                    "district": subgrantee.district,
                }

            return Response(data, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response(
                {"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except (Grant.DoesNotExist, GrantApplication.DoesNotExist, GrantApplicationReview.DoesNotExist, SubgranteeProfile.DoesNotExist):
            return Response(
                {"error": "Related data not found"}, status=status.HTTP_404_NOT_FOUND
            )


class UnreadNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        # Determine notification type based on is_staff
        if user.is_staff:
            # Admin users receive 'admin' notifications
            notifications = Notification.objects.filter(
                user=user, is_read=False, notification_type='admin'
            )
        else:
            # Non-admin users (subgrantees) receive 'grantee' notifications
            notifications = Notification.objects.filter(
                user=user, is_read=False, notification_type='grantee'
            )

        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

class NotificationsAll(APIView):
    permission_classes= [IsAuthenticated]
    def get(self, request, *args, **kwargs):
            user = request.user
            if user.is_staff:
                notifications = Notification.objects.filter(notification_type='admin').order_by('-timestamp')
            else:
                notifications = Notification.objects.filter(notification_type='grantee').order_by('-timestamp')

            serializer = NotificationSerializer(notifications, many=True)
            return Response(serializer.data)    

class UserNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, *args, **kwargs):
        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if request.user != user and not request.user.is_staff:
            return Response({"error": "You do not have permission to view this user's notifications"}, status=status.HTTP_403_FORBIDDEN)

        if request.user.is_staff:
            notifications = Notification.objects.filter(user=user, notification_type='admin').order_by('-timestamp')
        else:
            notifications = Notification.objects.filter(user=user, notification_type='grantee').order_by('-timestamp')

        if notifications.exists():
            serializer = NotificationSerializer(notifications, many=True)
            return Response(serializer.data)
        else:
            return Response({"message": "No notifications found for this user"}, status=status.HTTP_404_NOT_FOUND)


class NotificationReviewActionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:

            notification = Notification.objects.get(pk=pk)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)

        if notification.notification_category == 'grant_review' and notification.review.status == 'negotiate':

            action = request.data.get('action')


            if action not in ['approve', 'decline']:
                return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

            notification.is_read = True
            notification.review_recommendation = 'approved' if action == 'approve' else 'declined'
            notification.save()

            serializer = NotificationSerializer(notification)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid notification category or review status'}, status=status.HTTP_400_BAD_REQUEST)
