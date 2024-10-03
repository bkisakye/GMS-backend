import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
from django.utils.html import escape as html_escape
from authentication.models import CustomUser

logger = logging.getLogger(__name__)


def send_formatted_email(subject, message, recipient_list):
    plain_message = strip_tags(message)
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=message,
            fail_silently=False,
        )
        logger.info(f"Email sent successfully to {recipient_list}")
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")


@receiver(post_save, sender=Notification)
def notify_admin_on_grant_review_action(sender, instance, created, **kwargs):
    logger.info(f"Signal received for Notification ID: {instance.id}")
    logger.info(
        f"Created: {created}, Category: {instance.notification_category}, Status: {instance.status}")

    if created and instance.notification_category == 'grant_review':
        logger.info("Notification is for grant review and is newly created")

        if instance.review:
            logger.info(
                f"Associated review found. Recommendation: {instance.review}")
        else:
            logger.info("No associated review found")

        if instance.review and instance.review.review_recommendation == 'negotiate':
            logger.info("Review recommendation is 'negotiate'")

            if instance.status in ['approved', 'declined']:
                logger.info(
                    f"Status is {instance.status}, proceeding with admin notification")

                admin_users = CustomUser.objects.filter(is_staff=True)
                recipient_list = [admin.email for admin in admin_users]
                subject = f"Grant Review Notification: {instance.status.capitalize()} (Previously Negotiate)"
                message = f"""
                A grant review that was previously in 'negotiate' status has been {instance.status}.
                Notification ID: {instance.id}
                Previous Status: Negotiate
                New Status: {instance.status.capitalize()}
                Grant Application: {instance.application}
                Subgrantee: {instance.subgrantee}
                """

                try:
                    admin_notification = Notification.objects.create(
                        notification_type='admin',
                        notification_category='grant_review',
                        text=f"Grant review {instance.status}: {instance.application}",
                        status='pending',
                        application=instance.application,
                        subgrantee=instance.subgrantee,
                        review=instance.review,
                    )
                    admin_notification.user.set(admin_users)
                    logger.info(
                        f"Admin notification created: {admin_notification.id}")
                except Exception as e:
                    logger.error(
                        f"Failed to create admin notification: {str(e)}")

                # Send email to admins
                send_formatted_email(
                    subject=subject,
                    message=html_escape(message),
                    recipient_list=recipient_list
                )
            else:
                logger.info(
                    f"Status is {instance.status}, not creating admin notification")
        else:
            logger.info(
                "Review recommendation is not 'negotiate' or no review associated")
    else:
        logger.info(
            "Notification is not for grant review or is not newly created")
