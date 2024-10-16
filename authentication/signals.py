from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
from .models import CustomUser
from notifications.models import Notification
from subgrantees.models import SubgranteeProfile
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
    # Check if the user was just created and is not staff or approved
    if created and not instance.is_staff and not instance.is_approved:
        # Create or get the SubgranteeProfile associated with the user
        subgrantee_profile, created_profile = SubgranteeProfile.objects.get_or_create(
            user=instance)

        # Proceed only if a new profile was created
        if created_profile:
            # Ensure the organisation_name is set
            if instance.organisation_name:
                # Create the notification for the new subgrantee
                notification = Notification.objects.create(
                    notification_type='admin',
                    notification_category='new_subgrantee',
                    text=f"A new grantee has signed up: {instance.organisation_name}",
                    subgrantee=subgrantee_profile
                )

                # Associate this notification with all admin users
                admin_users = CustomUser.objects.filter(is_staff=True)
                notification.user.set(admin_users)

                # Prepare and send the formatted email to admin users
                html_content = f"""
                <html>
                <body>
                <h2>New Subgrantee Signup</h2>
                <p>A new subgrantee has signed up: {html.escape(instance.organisation_name)}.</p>
                <p>Please log in and review it.</p>
                </body>
                </html>
                """
                send_formatted_email(
                    subject="New Subgrantee Signup",
                    html_content=html_content,
                    recipient_list=[admin.email for admin in admin_users]
                )
            else:
                print(
                    f"Warning: organisation_name is None for the new user {instance.email}. Notification not sent.")
