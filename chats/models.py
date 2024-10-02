from django.db import models
from authentication.models import CustomUser


class ChatRoom(models.Model):
    subgrantee = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='subgrantee_chat_room')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat Room for {self.subgrantee.organization_name}"


class Message(models.Model):
    room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)