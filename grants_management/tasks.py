from celery import shared_task
from django.utils import timezone
from grants_management.models import Grant, FinancialReport, GrantAccount, Disbursement
import logging
from django.db import transaction
from datetime import timedelta
from decimal import Decimal
from django.core.management import call_command
from notifications.models import Notification


logger = logging.getLogger(__name__)


@shared_task(bind=True, rate_limit='1/m')
def deactivate_expired_grants(self):
    
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
    logger.info(f'Task {self.request.id} started')
    today = timezone.now().date()

    try:
        with transaction.atomic():
            dead_grants = Grant.objects.filter(
                end_date__lte=today, is_open=True)
            closed_count = dead_grants.update(is_open=False)

            # Log individual grant closures
            for grant in dead_grants:
                logger.info(f"Closed grant: {grant.name} (ID: {grant.id})")

        logger.info(
            f'Task {self.request.id} finished successfully. Closed {closed_count} grants.')
        return f"Closed {closed_count} grants."

    except Exception as e:
        logger.error(f"Error in task {self.request.id}: {str(e)}")
        # Re-raise the exception so Celery knows the task failed
        raise




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

    reminders_sent = 0

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
                notification_category='reminders',
                notification_type='grantee',
                text=f"Reminder: Your progress report for grant '{grant.name}' is due on {next_report_date.strftime('%Y-%m-%d')}.",
            )
            notification.user.add(user)

            try:
                send_mail(
                    'Progress Report Reminder',
                    f"Dear {user.organisation_name},\n\nThis is a reminder that your progress report for the grant '{grant.name}' is due on {next_report_date.strftime('%Y-%m-%d')}. Please ensure it is submitted on time.\n\nBest regards,\nGrant Management Team",
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                reminders_sent += 1
            except Exception as e:
                logger.error(f"Failed to send email to {user.email}: {str(e)}")

    logger.info(
        f"Reminder process completed. Sent {reminders_sent} reminders out of {accounts_due_for_reports.count()} active grant accounts.")
    return f"Reminder process completed. Sent {reminders_sent} reminders out of {accounts_due_for_reports.count()} active grant accounts."


@shared_task
def create_disbursement_reminders():
    logger.info("Starting disbursement reminder task.")
    now = timezone.now()

    # Fetch accounts with disbursements where the budget balance is greater than 0
    accounts_with_disbursements = Disbursement.objects.values('grant_account').annotate(
        total_disbursed=Sum('disbursement_amount'),
        budget_balance=F(
            'grant_account__budget_total__budget_total') - Sum('disbursement_amount')
    ).filter(
        budget_balance__gt=0  # Budget balance should not be zero
    )

    reminders_sent = 0

    for account in accounts_with_disbursements:
        grant_account_id = account['grant_account']
        total_disbursed_amount = account['total_disbursed']
        budget_total_amount = GrantAccount.objects.get(
            id=grant_account_id).budget_total.budget_total

        # Check if the total disbursed amount is not equal to the budget total
        if total_disbursed_amount != budget_total_amount:
            for admin in User.objects.filter(is_staff=True):
                # Create a notification for the admin
                notification = Notification.objects.create(
                    notification_category='reminders',
                    notification_type='admin',
                    text=f"Reminder: The account '{grant_account_id}' has pending balances. Please remember to process disbursement for the account.",
                )
                notification.user.add(admin)

                # Send an email to the admin
                try:
                    send_mail(
                        'Disbursement Reminder',
                        f"Dear {admin.organisation_name},\n\nThis is a reminder that the account '{grant_account_id}' has pending balances. Please remember to process disbursement for the account.\n\nBest regards,\nGrant Management Team",
                        settings.DEFAULT_FROM_EMAIL,
                        [admin.email],
                        fail_silently=False,
                    )
                    reminders_sent += 1
                except Exception as e:
                    logger.error(
                        f"Failed to send email to {admin.email}: {str(e)}")

    logger.info(
        f"Disbursement reminder process completed. Sent {reminders_sent} reminders.")
    return f"Disbursement reminder process completed. Sent {reminders_sent} reminders."
