from django.core.mail import send_mail
from django.conf import settings
from django.db.models import F
import logging
from authentication.models import CustomUser
from grants_management.models import Notification

logger = logging.getLogger(__name__)


def send_subgrantee_reminders():
    reminders_sent = 0

    # Fetch unapproved subgrantees
    unapproved_subgrantees = CustomUser.objects.filter(
        is_approved__isnull=True)

    # Fetch all admins (staff users)
    admins = CustomUser.objects.filter(is_staff=True)

    if unapproved_subgrantees.exists() and admins.exists():
        subgrantee_count = unapproved_subgrantees.count()

        # Improved notification text
        notification_text = (
            f"Reminder: {subgrantee_count} subgrantee{'s' if subgrantee_count > 1 else ''} "
            f"await approval. Please review and approve the pending applications."
        )

        # Create a notification for all admins
        notification = Notification.objects.create(
            notification_category='reminders',
            notification_type='admin',
            text=notification_text,
        )
        # Add all admins to the notification
        notification.user.add(*admins)

        # Improved email text
        email_subject = 'Subgrantee Approval Reminder'
        email_message = (
            f"Dear Admin,\n\n"
            f"This is a reminder that {subgrantee_count} subgrantee{'s' if subgrantee_count > 1 else ''} "
            f"have not yet been approved. Please log in to the system and review the pending applications.\n\n"
            f"Best regards,\n"
            f"Grant Management Team"
        )

        # Send a single email to all admins
        try:
            admin_emails = admins.values_list('email', flat=True)
            send_mail(
                email_subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,  # Send to all admin emails
                fail_silently=False,
            )
            reminders_sent += 1
        except Exception as e:
            logger.error(f"Failed to send email to admins: {str(e)}")

    logger.info(
        f"Subgrantee reminder process completed. Sent {reminders_sent} reminders."
    )

    return f"Subgrantee reminder process completed. Sent {reminders_sent} reminders."
