from django.db import models
from django.conf import settings
from subgrantees.models import SubgranteeProfile


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('admin', 'Admin'),
        ('grantee', 'Grantee'),
        # Add other types as needed
    )

    NOTIFICATION_CATEGORY = (
        ('new_grant', 'New Grant'),
        ('grant_application', 'Grant Application'),
        ('grant_review', 'Grant Review'),
        ('new_subgrantee', 'New Subgrantee'),
        ('grant_submission', 'Grant Submission'),
        ('status_report_due', 'Status Report Due'),
        ('status_report_submitted', 'Status Report Submitted'),
        ('status_report_reviewed', 'Status Report Reviewed'),
        ('disbursement_received', 'Disbursement Received'),
        ('request_review', 'Request Review'),
        ('financial_report', 'Financial Report'),
        ('requests', 'Requests'),
    )

    NOTIFICATION_STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    )

    REVIEW_RECOMMENDATION = (
        ('approve', 'Approve'),
        ('decline', 'Decline'),
        ('negotiate', 'Negotiate'),
    )

    user = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='notifications')
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES)
    notification_category = models.CharField(
        max_length=30, choices=NOTIFICATION_CATEGORY)
    text = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20, choices=NOTIFICATION_STATUS, default='pending')
    subgrantee = models.ForeignKey(
        'subgrantees.SubgranteeProfile', on_delete=models.CASCADE, null=True, blank=True)
    application = models.ForeignKey(
        'grants_management.GrantApplication', on_delete=models.CASCADE, null=True, blank=True)
    grant = models.ForeignKey(
        'grants_management.Grant', on_delete=models.CASCADE, null=True, blank=True)
    review = models.ForeignKey('grants_management.GrantApplicationReview',
                               on_delete=models.CASCADE, null=True, blank=True)
    uploads = models.ForeignKey('grants_management.GrantApplicationReviewDocument', on_delete=models.CASCADE, null=True, blank=True)                           
    review_recommendation = models.CharField(
        max_length=20, choices=REVIEW_RECOMMENDATION, null=True, blank=True)


    def __str__(self):
        return self.text
