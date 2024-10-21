from django.core.management.base import BaseCommand
# Import the utility function
from grants_management.utilis.disbursement_reminders import send_disbursement_reminders


class Command(BaseCommand):
    help = 'Test sending disbursement reminders'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS(
            'Starting disbursement reminder test...'))
        result = send_disbursement_reminders()
        self.stdout.write(self.style.SUCCESS(result))
