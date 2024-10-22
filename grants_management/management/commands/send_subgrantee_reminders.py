from django.core.management.base import BaseCommand
from grants_management.utilis.subgrantess_reminders import send_subgrantee_reminders

class Command(BaseCommand):
    help = 'Testing sending subgrantee reminders'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS(
            'Starting disbursement reminder test..'
        ))
        result = send_subgrantee_reminders_task()
        self.stdout.write(self.style.SUCCESS(result))