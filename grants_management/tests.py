import time
from django.test import TestCase
from authentication.models import CustomUser
from grants_management.models import GrantAccount, Disbursement, Notification
# Replace 'myapp' with the actual app name
from grants_management.tasks import send_disbursement_reminders


class DisbursementReminderTest(TestCase):

    def setUp(self):
        # Create test data: Admin user and GrantAccount
        self.admin = CustomUser.objects.create(
            email='admin@example.com', is_staff=True)
        self.grant_account = GrantAccount.objects.create(
            account_holder=self.admin,  # Replace with the appropriate fields
            budget_total=10000
        )
        Disbursement.objects.create(
            grant_account=self.grant_account, disbursement_amount=5000)

    def test_async_disbursement_reminder_task(self):
        # Trigger the Celery task asynchronously
        task = send_disbursement_reminders.delay()

        # Wait for the task to complete
        while not task.ready():
            time.sleep(1)  # Check task status every second

        # Assert that the task completed successfully
        self.assertEqual(task.status, 'SUCCESS')

        # Assert that a Notification was created for the admin
        notifications = Notification.objects.filter(user=self.admin)
        self.assertEqual(notifications.count(), 1)

        # Check that an email was sent to the admin
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertIn(self.admin.email, outbox[0].to)
