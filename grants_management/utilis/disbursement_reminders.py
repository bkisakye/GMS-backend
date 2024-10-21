from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import F, Sum
from datetime import timedelta
import logging
from authentication.models import CustomUser
from grants_management.models import GrantAccount, Notification, Disbursement

logger = logging.getLogger(__name__)


def send_disbursement_reminders():
    reminders_sent = 0
    accounts_with_disbursements = Disbursement.objects.values('grant_account').annotate(
        total_disbursed=Sum('disbursement_amount'),
        budget_balance=F(
            'grant_account__budget_total__budget_total') - Sum('disbursement_amount')
    ).filter(
        budget_balance__gt=0  # Ensure correct lookup, 'gt' for greater than
    )

    if not accounts_with_disbursements.exists():
        logger.info('No accounts with pending disbursements.')
        return "No accounts with pending disbursements."

    # Fetch all admins (staff users)
    admins = CustomUser.objects.filter(is_staff=True)

    if not admins.exists():
        logger.warning('No admins found to send notifications.')
        return "No admins found to send notifications."

    for account in accounts_with_disbursements:
        grant_account_id = account['grant_account']
        total_disbursed_amount = account['total_disbursed']

        # Fetch the GrantAccount instance to get related fields
        grant_account = GrantAccount.objects.get(id=grant_account_id)
        budget_total_amount = grant_account.budget_total.budget_total

        # Check if the total disbursed amount is less than the budget total
        if total_disbursed_amount != budget_total_amount:
            notification_text = (
                f"Reminder: The account for '{grant_account.account_holder.organisation_name}' - "
                f"'{grant_account.grant.name}' has pending balances. Please process disbursement for the account."
            )

            # Create a single notification for all admins
            notification = Notification.objects.create(
                notification_category='reminders',
                notification_type='admin',
                text=notification_text,
            )
            # Add all admins to the notification
            notification.user.add(*admins)

            # Send a single email to all admins
            try:
                admin_emails = admins.values_list('email', flat=True)
                send_mail(
                    'Disbursement Reminder',
                    f"This is a reminder that the account for "
                    f"'{grant_account.account_holder.organisation_name}' - '{grant_account.grant.name}' "
                    "has pending balances. Please process disbursement for the account.\n\nBest regards,\nGrant Management Team",
                    settings.DEFAULT_FROM_EMAIL,
                    admin_emails,  # Send to all admin emails
                    fail_silently=False,
                )
                reminders_sent += 1
            except Exception as e:
                logger.error(f"Failed to send email to admins: {str(e)}")

    logger.info(
        f"Disbursement reminder process completed. Sent {reminders_sent} reminders.")
    return f"Disbursement reminder process completed. Sent {reminders_sent} reminders."
