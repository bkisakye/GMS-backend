from celery import shared_task
from django.utils import timezone
from grants_management.models import Grant, FinancialReport, GrantAccount, Disbursement
import logging
from django.db import transaction
from datetime import timedelta
from decimal import Decimal
from django.core.management import call_command
from notifications.models import Notification
from grants_management.utilis.report_reminders import process_report_reminders
from grants_management.utilis.subgrantess_reminders import send_subgrantee_reminders
from grants_management.utilis.disbursement_reminders import send_disbursement_reminders


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
    reminders_sent, total_accounts, next_report_dates = process_report_reminders()
    return f"Reminder process completed. Sent {reminders_sent} reminders out of {total_accounts} active grant accounts."


@shared_task  # Mark this function as a Celery task
def send_disbursement_reminders_task():
    reminders_sent = send_disbursement_reminders()
    return f"Reminder process completed. Sent {reminders_sent} reminders"

    
@shared_task
def send_subgrantee_reminders_task():
    # Call the utility function directly
    reminders_sent = send_subgrantee_reminders()
    return reminders_sent

