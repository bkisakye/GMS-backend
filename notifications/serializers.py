from rest_framework import serializers
from .models import Notification
from authentication.serializers import CustomUserSerializer
from grants_management.serializers import GrantApplicationSerializer, GrantApplicationReviewSerializer, ProgressReportSerializer, RequestReviewSerializer, GrantApplicationReviewDocumentSerializer, GrantSerializer
from django.contrib.auth import get_user_model
from chats.serializers import MessageSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'fname', 'lname', 'organisation_name', 'is_approved')

class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=True)
    application = GrantApplicationSerializer(read_only=True)
    review = GrantApplicationReviewSerializer(read_only=True)
    progress_report = ProgressReportSerializer(read_only=True)
    chats = MessageSerializer(read_only=True)
    requests = RequestReviewSerializer(read_only=True)
    uploads = GrantApplicationReviewDocumentSerializer(read_only=True)
    grant = GrantSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ('id', 'user', 'notification_type', 'notification_category', 'text',
                  'timestamp', 'is_read', 'application', 'review', 'subgrantee', 'grant', 'review_recommendation', 'progress_report','chats', 'requests', 'uploads',)
