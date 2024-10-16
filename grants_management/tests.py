from django.test import TestCase
from django.core import mail
from unittest.mock import patch
from grants_management.models import GrantAccount, Disbursement
from notifications.models import Notification
from grants_management.tasks import create_disbursement_reminders
# Import to get the custom user model
from django.contrib.auth import get_user_model
from decimal import Decimal


class DisbursementReminderTaskTests(TestCase):
    def setUp(self):
        # Get the custom user model
        CustomUser = get_user_model()

        # Create a user (admin) using only the email and password
        self.admin_user = CustomUser.objects.create_user(
            email='admin@example.com',  # Only use email
            password='password'
        )

        # Create a GrantAccount
        self.grant_account = GrantAccount.objects.create(
            admin=self.admin_user  # Assuming the GrantAccount has an admin field
        )

        # Create a Disbursement linked to the GrantAccount
        self.disbursement = Disbursement.objects.create(
            grant_account=self.grant_account,
            disbursement_amount=Decimal('1000.00'),  # Example value
            # Set other fields as needed
        )

        # Set a budget total (assumed to be related to grant_account)
        self.grant_account.budget_total.budget_total = Decimal('1500.00')
        self.grant_account.budget_total.save()

    @patch('grants_management.tasks.send_mail')  # Mock send_mail
    def test_create_disbursement_reminders(self, mock_send_mail):
        # Call the task
        result = create_disbursement_reminders()

        # Check if a notification was created
        notifications = Notification.objects.filter(
            notification_category='reminders')
        self.assertEqual(notifications.count(), 1)

        # Check if the email was sent
        self.assertEqual(mock_send_mail.call_count, 1)

        # Verify the email content
        self.assertIn("Reminder: The account",
                      mock_send_mail.call_args[0][1])  # Subject
        self.assertIn(str(self.grant_account.id),
                      mock_send_mail.call_args[0][1])  # Body content

        # Check the result of the task
        self.assertIn("Sent 1 reminders", result)

    def tearDown(self):
        # Clean up the test data if needed
        pass
