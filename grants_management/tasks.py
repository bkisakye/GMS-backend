from celery import shared_task
from django.utils import timezone
from grants_management.models import Grant, FinancialReport, GrantAccount
import logging
from django.db import transaction
from datetime import timedelta
from decimal import Decimal
from django.core.management import call_command
from notifications.models import Notification


logger = logging.getLogger(__name__)


@shared_task(bind=True, rate_limit='1/m')
def deactivate_expired_grants(self):
    logger.info(f'Task {self.request.id} started')
    now = timezone.now().date()
    expired_grants = Grant.objects.filter(
        application_deadline__lt=now, is_active=True)
    with transaction.atomic():
        for grant in expired_grants:
            grant.is_active = False
            try:
                grant.save()
                logger.info(f"Deactivated grant: {grant.name}")
            except Exception as e:
                logger.error(
                    f"Error deactivating grant {grant.name}: {str(e)}")
    logger.info(f'Task {self.request.id} finished')
    return f"Deactivated {expired_grants.count()} expired grants."


@shared_task(bind=True, rate_limit='1/m')
def close_dead_grants(self):
    now = timezone.now().date()
    dead_grants = Grant.objects.filter(end_date__lt=now, is_open=True)

    with transaction.atomic():
        closed_count = 0
        for grant in dead_grants:
            grant.is_open = False
            try:
                grant.save()
                closed_count += 1
            except Exception as e:
                # Optionally, log the exception here
                print(f"Error closing grant {grant.id}: {e}")

    return f"Closed {closed_count} grants."


@shared_task
def generate_monthly_financial_report(grant_account_id=None, date=None):
    logger.info(
        f"Starting generate_monthly_financial_report for account {grant_account_id} and date {date}")

    if date is None:
        current_date = timezone.now().date()
    else:
        current_date = date

    last_month = current_date.replace(day=1) - timedelta(days=1)

    try:
        if grant_account_id:
            grant_accounts = [GrantAccount.objects.get(id=grant_account_id)]
        else:
            grant_accounts = GrantAccount.objects.all()

        for grant_account in grant_accounts:
            logger.info(f"Generating report for account {grant_account}")
            report = generate_financial_report(grant_account, last_month)
            logger.info(f"Report generated: {report}")

        logger.info("Finished generate_monthly_financial_report")
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise  # Re-raise the exception after logging


def convert_decimal_to_float(data):
    """Recursively convert all Decimals in a dictionary to floats."""
    if isinstance(data, dict):
        return {k: convert_decimal_to_float(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_decimal_to_float(item) for item in data]
    elif isinstance(data, Decimal):
        return float(data)
    return data


def generate_financial_report(grant_account, end_date):
    logger.info(
        f"Generating financial report for account {grant_account} and date {end_date}")

    fiscal_year = end_date.year  # Adjust this if your fiscal year is different

    report = {
        'grant_account': str(grant_account),
        'report_date': end_date.strftime('%Y-%m-%d'),
        'fiscal_year': fiscal_year,
        'budget_summary': grant_account.get_budget_summary(fiscal_year),
        'allocations': list(grant_account.allocations.filter(allocation_date__lte=end_date).values('amount', 'allocation_date', 'description')),
        'fiscal_year_report': grant_account.generate_fiscal_year_report(),
    }

    # Convert Decimal fields to float
    report = convert_decimal_to_float(report)

    # Save the report
    financial_report, created = FinancialReport.objects.update_or_create(
        grant_account=grant_account,
        report_date=end_date,
        defaults={
            'fiscal_year': fiscal_year,
            'report_data': report
        }
    )

    logger.info(
        f"Financial report {'created' if created else 'updated'} with id {financial_report.id}")
    return report


@shared_task
def send_report_reminders():
    now = timezone.now()
    reminder_window = now + timedelta(days=1)

    accounts_due_for_reports = GrantAccount.objects.filter(
        grant__reporting_time__in=['monthly',
                                   'quarterly', 'annually', 'weekly'],
        grant__end_date__gte=now.date(),
        status='active'
    ).select_related('grant', 'account_holder')

    for account in accounts_due_for_reports:
        user = account.account_holder
        grant = account.grant

        # Calculate the next reporting date based on the grant's reporting time
        if grant.reporting_time == 'monthly':
            next_report_date = (now.replace(day=1) +
                                timedelta(days=32)).replace(day=1)
        elif grant.reporting_time == 'quarterly':
            next_report_date = (now.replace(day=1) +
                                timedelta(days=93)).replace(day=1)
        elif grant.reporting_time == 'annually':
            next_report_date = now.replace(year=now.year + 1, month=1, day=1)
        elif grant.reporting_time == 'weekly':
            next_report_date = now + timedelta(days=(7 - now.weekday()))
        else:
            continue  # Skip if reporting time is not recognized

        # Check if the next report date is within the reminder window
        if now.date() <= next_report_date.date() <= reminder_window.date():
            notification = Notification.objects.create(
                user=user,
                notification_category='reminders',
                notification_type='grantee',
                text=f"Reminder: Your progress report for grant '{grant.name}' is due on {next_report_date.strftime('%Y-%m-%d')}.",
            )

            try:
                send_mail(
                    'Progress Report Reminder',
                    f"Dear {user.get_full_name()},\n\nThis is a reminder that your progress report for the grant '{grant.name}' is due on {next_report_date.strftime('%Y-%m-%d')}. Please ensure it is submitted on time.\n\nBest regards,\nGrant Management Team",
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log the error for debugging
                print(f"Failed to send email to {user.email}: {e}")

    return f"Reminder process completed. Checked {accounts_due_for_reports.count()} active grant accounts."
