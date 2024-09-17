from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from .models import CustomUser
from notifications.models import Notification
from subgrantees.models import SubgranteeProfile
from django.utils.html import strip_tags
import html


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

@receiver(post_save, sender=CustomUser)
def create_grantee_signup_notification(sender, instance, created, **kwargs):
    if created and not instance.is_staff:
        # Use get_or_create to avoid duplicate entries
        subgrantee_profile, created_profile = SubgranteeProfile.objects.get_or_create(
            user=instance)

        if created_profile:
            # Create a notification only if a new profile was created
            notification = Notification.objects.create(
                notification_type='admin',
                notification_category='new_subgrantee',
                text=f"A new grantee has signed up: {instance.organisation_name}",
                subgrantee=subgrantee_profile
            )

            # Associate this notification with all admin users
            admin_users = CustomUser.objects.filter(is_staff=True)
            notification.user.set(admin_users)

            html_content = f"""
            <html>
            <body>
            <h2>New Subgrantee Signup</h2>
            <p>A new subgrantee has signed up: {html.escape(instance.organisation_name)} </p>
            <p>Please login and review it..</p>
            </body>
            </html>
            """
            send_formatted_email(
                subject=f"New Subgrantee Signup",
                html_content=html_content,
                recipient_list=[admin.email for admin in admin_users]
            )

