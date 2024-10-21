from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import F, OuterRef, Subquery
from django.template.loader import render_to_string
from datetime import timedelta
import logging

from grants_management.models import GrantAccount, ProgressReport, Notification

logger = logging.getLogger(__name__)


def calculate_next_report_date(last_report_date, reporting_time):
    if reporting_time == 'weekly':
        return last_report_date + timedelta(weeks=1)
    elif reporting_time == 'monthly':
        return (last_report_date.replace(day=1) + timedelta(days=32)).replace(day=1)
    elif reporting_time == 'quarterly':
        return (last_report_date.replace(day=1) + timedelta(days=93)).replace(day=1)
    elif reporting_time == 'annually':
        return last_report_date.replace(year=last_report_date.year + 1)


def send_reminder(user, grant, next_report_date):
    try:
        # Create notification
        notification_text = (
            f"Reminder: Your progress report for the grant '{grant.name}' "
            f"is due on {next_report_date.strftime('%Y-%m-%d')}. Please ensure it is submitted on time."
        )

        notification = Notification.objects.create(
            notification_category='reminders',
            notification_type='grantee',
            text=notification_text,
        )
        notification.user.add(user)

        # Prepare email context
        context = {
            'user': user,
            'grant': grant,
            'next_report_date': next_report_date,
        }
        email_body = render_to_string('emails/report_reminder.txt', context)
        email_subject = f"Progress Report Reminder for {grant.name}"

        # Send email
        send_mail(
            email_subject,
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(
            f"Failed to send reminder to {user.email} for grant {grant.name}: {str(e)}")
        return False


def process_report_reminders():
    now = timezone.now()
    reminder_window = now + timedelta(days=1)

    # Fetch last report dates for each grant account
    last_report = ProgressReport.objects.filter(
        grant_account=OuterRef('pk')
    ).order_by('-report_date').values('report_date')[:1]

    accounts_due_for_reports = GrantAccount.objects.annotate(
        last_report_date=Subquery(last_report)
    ).filter(
        grant__reporting_time__in=[
            'weekly', 'monthly', 'quarterly', 'annually'],
        grant__end_date__gte=now.date(),
        status='active'
    ).select_related('grant', 'account_holder')

    reminders_sent = 0
    next_report_dates = []  # List to store next report dates

    for account in accounts_due_for_reports:
        user = account.account_holder
        grant = account.grant
        last_report_date = account.last_report_date or grant.start_date

        next_report_date = calculate_next_report_date(
            last_report_date, grant.reporting_time)
        next_report_dates.append(
            (user.email, grant.name, next_report_date))  # Store for logging

        # Define the reminder days
        reminder_days = [5, 2, 0]  # Days before the due date to send reminders

        # Check if a report has already been submitted
        report_submitted = ProgressReport.objects.filter(
            grant_account=account, report_date__date=next_report_date).exists()

        if not report_submitted:
            for days in reminder_days:
                reminder_date = next_report_date - timedelta(days=days)
                if now.date() == reminder_date.date():
                    if send_reminder(user, grant, next_report_date):
                        reminders_sent += 1
                        break  # Break after sending one reminder to avoid sending multiple

    logger.info(
        f"Reminder process completed. Sent {reminders_sent} reminders out of {accounts_due_for_reports.count()} active grant accounts.")

    # Return the number of reminders sent, total accounts, and the next report dates
    return reminders_sent, accounts_due_for_reports.count(), next_report_dates
