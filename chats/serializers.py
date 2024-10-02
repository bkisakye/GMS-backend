from rest_framework import serializers
from .models import ChatRoom, Message
from authentication.serializers import CustomUserSerializer


class ChatRoomSerializer(serializers.ModelSerializer):
    subgrantee = CustomUserSerializer(read_only=True)
    class Meta:
        model = ChatRoom
        fields = ['id', 'subgrantee', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'content', 'timestamp']
