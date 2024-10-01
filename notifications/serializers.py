from rest_framework import serializers
from .models import Notification
from authentication.serializers import CustomUserSerializer
from grants_management.serializers import GrantApplicationSerializer, GrantApplicationReviewSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'fname', 'lname', 'organisation_name', 'is_approved')

class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=True)
    application = GrantApplicationSerializer(read_only=True)
    review = GrantApplicationReviewSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ('id', 'user', 'notification_type', 'notification_category', 'text',
                  'timestamp', 'is_read', 'application', 'review', 'subgrantee', 'grant', 'review_recommendation')
