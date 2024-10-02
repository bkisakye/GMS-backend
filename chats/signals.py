from django.db.models.signals import post_save
from django.dispatch import receiver
from authentication.models import CustomUser
from .models import ChatRoom

@receiver(post_save, sender=CustomUser)
def create_chat_room(sender, instance, created, **kwargs):
    if instance.is_approved and not instance.is_staff:
        if created or not hasattr(instance, 'subgrantee_chat_room'):
            ChatRoom.objects.create(subgrantee=instance)
    