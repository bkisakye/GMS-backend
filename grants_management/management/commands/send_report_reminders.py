from django.core.management.base import BaseCommand
from grants_management.models import GrantAccount, ProgressReport
from datetime import timedelta
from django.utils import timezone
import logging
from grants_management.utilis.report_reminders import process_report_reminders

# Import your process_report_reminders function here

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sends reminders for due progress reports.'

    def handle(self, *args, **options):
        self.stdout.write("Starting to send report reminders...")

        # Call the function that processes the reminders
        reminders_sent, total_accounts, next_report_dates = process_report_reminders()

        # Log next report dates for debugging
        for email, grant_name, next_date in next_report_dates:
            self.stdout.write(
                f"User: {email}, Grant: {grant_name}, Next Report Date: {next_date.strftime('%Y-%m-%d')}")

        self.stdout.write(self.style.SUCCESS(
            f'Sent {reminders_sent} reminders out of {total_accounts} active grant accounts.'))
