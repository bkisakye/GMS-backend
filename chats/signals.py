from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import strip_tags
from django.conf import settings
from authentication.models import CustomUser
from .models import ChatRoom, Message
from notifications.models import Notification


def send_formatted_email(subject, html_content, recipient_list):
    plain_message = strip_tags(html_content)
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        html_message=html_content,
        fail_silently=False,
    )


def create_notification(user, notification_type, notification_category, text, **kwargs):
    notification = Notification.objects.create(
        notification_type=notification_type,
        notification_category=notification_category,
        text=text,
        **kwargs
    )
    notification.user.add(user)
    return notification


@receiver(post_save, sender=CustomUser)
def create_chat_room(sender, instance, created, **kwargs):
    if instance.is_approved and not instance.is_staff:
        if created or not hasattr(instance, 'subgrantee_chat_room'):
            ChatRoom.objects.create(subgrantee=instance)


@receiver(post_save, sender=Message)
def notify_admin_or_subgrantee_on_new_message(sender, instance, created, **kwargs):
    admins = CustomUser.objects.filter(is_staff=True)
    if created:
        if instance.room.subgrantee == instance.sender:
            # Notify admins
            notification = Notification.objects.create(
                notification_type='admin',
                notification_category='messages',
                text=f"New message from {instance.sender.organisation_name}",
                chats=instance,
                
            )
            notification.user.set(admins)

        else:
            # Notify subgrantee
            notification = Notification.objects.create(
                notification_type='grantee',
                notification_category='messages',
                text=f"New message from {instance.sender.email}",
                chats=instance,
            
            )
            notification.user.add(instance.room.subgrantee)
