# grants_management/management/commands/send_report_reminder.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from grants_management.models import GrantAccount, ProgressReport


class Command(BaseCommand):
    help = 'Sends reminders to subgrantees for submitting progress reports'

    def handle(self, *args, **options):
        today = timezone.now().date()

        for grant_account in GrantAccount.objects.all():
            reporting_time = grant_account.grant.reporting_time
            status_reports = ProgressReport.objects.filter(
                grant_account=grant_account)
            last_report = status_reports.order_by('-report_date').first()

            if self.should_send_reminder(reporting_time, last_report, today):
                self.send_reminder(grant_account)

    def should_send_reminder(self, reporting_time, last_report, today):
        if not last_report:
            return True

        last_report_date = last_report.report_date.date()
        days_since_last_report = (today - last_report_date).days

        if reporting_time == 'weekly' and days_since_last_report >= 7:
            return True
        elif reporting_time == 'monthly' and days_since_last_report >= 30:
            return True
        elif reporting_time == 'annually' and days_since_last_report >= 365:
            return True

        return False

    def send_reminder(self, grant_account):
        subject = f"Reminder: Submit Progress Report for {grant_account.grant.name}"
        message = f"""
        Dear {grant_account.account_holder.organisation_name},

        This is a friendly reminder to submit your progress report for the grant: {grant_account.grant.name}.

        Please log in to your account and submit your report as soon as possible.

        Thank you for your cooperation.
        """
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = grant_account.account_holder.email

        send_mail(subject, message, from_email, [to_email])

        self.stdout.write(self.style.SUCCESS(f'Sent reminder to {to_email}'))
