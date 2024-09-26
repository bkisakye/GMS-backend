from django.db import models, transaction
from django.utils import timezone
from authentication.models import CustomUser
from subgrantees.models import SubgranteeProfile
from django.conf import settings
from notifications.models import Notification
from subgrantees.models import District
from django.conf import settings
from .utilis.budget import get_fiscal_years_for_grant, allocate_budget_for_grant
import uuid
import csv
from django.db.models import Sum
from decimal import Decimal
from django.core.exceptions import ValidationError


# Create your models here.


class GrantType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(('active'), default=True)
    details = models.TextField(blank=True)


class Donor(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(('active'), default=True)
    details = models.TextField(blank=True)


class SubgranteeCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(('active'), default=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Grant(models.Model):
    REPORTING_TIME = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
        ('weekly', 'Weekly'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    category = models.ForeignKey(GrantType, on_delete=models.CASCADE)
    donor = models.ForeignKey(
        Donor, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    application_deadline = models.DateField(null=True, blank=True)
    eligibility_details = models.TextField(blank=True)
    is_open = models.BooleanField(default=True)
    district = models.ManyToManyField(District, blank=True)
    kpis = models.JSONField(default=dict)
    reporting_time = models.CharField(
        max_length=20, choices=REPORTING_TIME)
    created = models.DateField(auto_now_add=True)  
    updated = models.DateField(auto_now=True)
    number_of_awards = models.IntegerField(default=0, blank=True, null=True)
    


    def get_fiscal_years(self):
        return get_fiscal_years_for_grant(self.start_date, self.end_date)

    def allocate_budget(self):
        return allocate_budget_for_grant(self)


class Section(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class SubSection(models.Model):
    title = models.CharField(max_length=255)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class DefaultApplicationQuestion(models.Model):
    QUESTION_TYPE = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio'),
        ('table', 'Table'),
    ]
    grant = models.ForeignKey(
        Grant, on_delete=models.CASCADE, blank=True, null=True)
    text = models.TextField()
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, blank=True, null=True)

    sub_section = models.ForeignKey(
        SubSection, on_delete=models.CASCADE, blank=True, null=True)
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE)
    choices = models.JSONField(
        blank=True, null=True
    )
    number_of_rows = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.text

    # grant_questions = DefaultApplicationQuestion.objects.filter(grant=grant or grant = null)


class GrantApplicationResponses(models.Model):
    grant = models.ForeignKey(
        Grant, on_delete=models.CASCADE, blank=True, null=True)
    question = models.ForeignKey(
        DefaultApplicationQuestion, on_delete=models.CASCADE, blank=True, null=True)
    answer = models.CharField(max_length=500, blank=True, null=True)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    choices = models.JSONField(
        blank=True, null=True
    )


class GrantApplication(models.Model):

    REVIEW_STATUS = [
        ("under_review", "Under Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("negotiate", "Negotiate"),
    ]

    subgrantee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    grant = models.ForeignKey(
        "Grant", on_delete=models.CASCADE, related_name="grant_management"
    )
    status = models.CharField(
        max_length=100, choices=REVIEW_STATUS, default="under_review")
    date_submitted = models.DateTimeField(auto_now_add=True)
    signed = models.BooleanField(default=False)
    updated = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    reviewed = models.BooleanField(default=False)
    last_review_date = models.DateTimeField(null=True, blank=True)
    last_response_date = models.DateTimeField(null=True, blank=True)


    @classmethod
    def get_compliance_percentange(cls):
        total_applications = cls.objects.count()
        signed_applications = cls.objects.filter(signed=True).count()

        if total_applications > 0:
           signed_percentage = (signed_applications / total_applications) * 100
        else:
            signed_percentage = 0
        return signed_percentage

def __str__(self):
    return f"Application made by {self.subgrantee.organisation_name} for {self.grant.name}"        

class GrantApplicationDocument(models.Model):
    application = models.ForeignKey(
        GrantApplication, on_delete=models.CASCADE, related_name='documents')
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='uploaded_documents')

    uploaded_at = models.DateTimeField(auto_now_add=True)
    documents = models.FileField(upload_to='grant_applications/')

    def __str__(self):
        return f"Document for Application {self.application.id} by {self.user.organisation_name}"


class TransformedGrantApplicationData(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    grant = models.ForeignKey(Grant, on_delete=models.CASCADE)
    transformed_data = models.JSONField(default=dict)  # Ensure default=dict

    def __str__(self):
        return f"{self.user.organisation_name} - {self.grant.name}"


class GrantApplicationReview(models.Model):
    application = models.ForeignKey(GrantApplication, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    review_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('negotiate', 'Negotiate'),
    ], default='pending')
    comments = models.TextField(blank=True, null=True)
    score = models.IntegerField()


    def __str__(self):
        return f"Review for {self.application.grant.name} by {self.reviewer.email}"

class GrantApplicationReviewDocument(models.Model):
    review = models.ForeignKey(GrantApplicationReview, on_delete=models.CASCADE)
    uploads = models.FileField(upload_to='grant_application_reviews/')

    def __str__(self):
        return f"Document for Review {self.review.id}"

class FilteredGrantApplicationResponse(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='filtered_responses')
    application = models.ForeignKey(
        GrantApplication, on_delete=models.CASCADE, related_name='filtered_responses')
    question = models.ForeignKey(
        DefaultApplicationQuestion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=500, blank=True, null=True)
    choices = models.JSONField(
        blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.question.text}"


class BudgetTotal(models.Model):
    grant = models.ForeignKey(Grant, on_delete=models.CASCADE)
    application = models.ForeignKey(GrantApplication, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    budget_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Budget Total for Application {self.application.id}"


class GrantAccount(models.Model):
    grant = models.ForeignKey(Grant, on_delete=models.CASCADE)
    account_holder = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    budget_total = models.ForeignKey(BudgetTotal, on_delete=models.CASCADE)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('pending_closeout', 'Pending Closeout'),
    ], default='active')
    disbursed = models.CharField(max_length=50, choices=[
        ('partially_disbursed', 'Partially Disbursed'),
        ('fully_disbursed', 'Fully Disbursed'),
        ('not_disbursed', 'Not Disbursed')
    ], default='not_disbursed')

    def __str__(self):
        return f"{self.grant.name} - {self.account_holder} - {self.budget_total.budget_total}"

    def get_budget_breakdown(self):
        fiscal_years = self.grant.get_fiscal_years()
        breakdown = {}
        for year in fiscal_years:
            items = self.budget_items.filter(fiscal_year=year)
            total_budgeted = items.aggregate(
                total=models.Sum('amount'))['total'] or 0
            breakdown[year] = total_budgeted
        return breakdown

    def generate_fiscal_year_report(self):
        fiscal_years = self.grant.get_fiscal_years()
        report = []
        for year in fiscal_years:
            budgeted = self.get_total_budgeted(fiscal_year=year)
            allocated = self.get_total_allocations()
            remaining = self.get_remaining_budget(fiscal_year=year)
            report.append({
                'fiscal_year': year,
                'budgeted': budgeted,
                'allocated': allocated,
                'remaining': remaining
            })
        return report

    def get_total_budgeted(self, fiscal_year=None):
        items = self.budget_items.all()
        if fiscal_year:
            items = items.filter(fiscal_year=fiscal_year)
        return items.aggregate(total=models.Sum('amount'))['total'] or 0

    def get_remaining_budget(self, fiscal_year=None):
        total_budget = self.budget_total.budget_total
        total_allocated = self.get_total_allocations()
        return total_budget - total_allocated

    def is_over_budget(self, fiscal_year=None):
        return self.get_remaining_budget(fiscal_year) < 0

    def get_total_allocations(self):
        return self.allocations.aggregate(total=models.Sum('amount'))['total'] or 0

    def get_budget_summary(self, fiscal_year=None):
        total_budget = self.budget_total.budget_total
        total_budgeted = self.get_total_budgeted(fiscal_year)
        total_allocated = self.get_total_allocations()
        remaining_amount = self.get_remaining_budget(fiscal_year)
        is_over_budget = self.is_over_budget(fiscal_year)

        return {
            'total_budget': total_budget,
            'total_allocated': total_allocated,
            'total_budgeted': total_budgeted,
            'remaining_amount': remaining_amount,
            'is_over_budget': is_over_budget
        }


class BudgetCategory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class BudgetItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    grant_account = models.ForeignKey(
        GrantAccount, on_delete=models.CASCADE, related_name='budget_items')
    category = models.ForeignKey(BudgetCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fiscal_year = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.category.name} - {self.amount} for {self.grant_account} (FY {self.fiscal_year})"


    def clean(self):
        if not self.grant_account:
            raise ValidationError("Related grant account does not exist.")

        total_budget = self.grant_account.budget_total.budget_total
        current_total = self.grant_account.budget_items.aggregate(
            total=models.Sum('amount'))['total'] or 0
        if current_total + self.amount > total_budget:
            raise ValidationError(
                "Budget item exceeds the grant's total budget.")

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class FundingAllocation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    grant_account = models.ForeignKey(
        GrantAccount, on_delete=models.CASCADE, related_name='allocations')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    allocation_date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    item = models.ForeignKey(
        BudgetItem, on_delete=models.CASCADE, related_name='allocations')
    reference_number = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)
    total_allocated = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, blank=True)

    class Meta:
        ordering = ['-allocation_date']

    def __str__(self):
        return f"Allocation of {self.amount} for {self.grant_account.account_holder} on {self.allocation_date}"

    def generate_total_allocated(self):
        total_allocated = self.grant_account.allocations.aggregate(
            total=models.Sum('amount'))['total'] or 0
        self.total_allocated = total_allocated
        self.save()

    def generate_reference_number(self):
        return f"FA-{uuid.uuid4().hex[:8].upper()}"

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()
        self.full_clean()
        super().save(*args, **kwargs)


class FinancialReport(models.Model):

    REVIEW_STATUS = (
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
    )

    REVIEWER_STATUS = (
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    grant_account = models.ForeignKey(
        GrantAccount, on_delete=models.CASCADE, related_name='financial_reports')
    report_date = models.DateField()
    fiscal_year = models.IntegerField()
    report_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    review_status = models.CharField(
        max_length=20, choices=REVIEW_STATUS, default='pending')
    review_comments = models.TextField(blank=True, null=True)
    reviewer_status = models.CharField(
        max_length=20, choices=REVIEWER_STATUS, default='pending')
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('grant_account', 'report_date')

    def __str__(self):
        return f"Financial Report for {self.grant_account} on {self.report_date}"


class ProgressReport(models.Model):
    STATUS_CHOICES = (
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('behind', 'Behind Schedule'),
        ('completed', 'Completed'),
    )

    REVIEW_STATUS = (
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
    )

    REVIEWER_STATUS = (
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    grant_account = models.ForeignKey(
        GrantAccount, on_delete=models.CASCADE, related_name='status_reports')
    report_date = models.DateTimeField(auto_now_add=True)
    completed_pkis = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    review_status = models.CharField(
        max_length=20, choices=REVIEW_STATUS, default='pending')
    review_comments = models.TextField(blank=True, null=True)
    reviewer_status = models.CharField(
        max_length=20, choices=REVIEWER_STATUS, default='pending')
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Status Report for {self.grant_account} - {self.report_date}"

    def calculate_status(self):
        total_kpis = len(self.grant_account.grant.kpis.split(','))
        completed = len(self.completed_pkis)
        self.progress_percentage = (completed / total_kpis) * 100

        if self.progress_percentage == 100:
            self.status = 'completed'
        elif self.progress_percentage >= 75:
            self.status = 'on_track'
        elif self.progress_percentage >= 50:
            self.status = 'at_risk'
        else:
            self.status = 'behind'

    def save(self, *args, **kwargs):
        self.calculate_status()

        if not self.pk or 'completed_pkis' in kwargs.get('update_fields', []):
            self.review_status = 'pending'
            self.reviewer = None
        super().save(*args, **kwargs)


class Disbursement(models.Model):
    grant_account = models.ForeignKey(
        GrantAccount, on_delete=models.CASCADE, related_name='disbursements')    
    disbursement_amount = models.DecimalField(max_digits=10, decimal_places=2)
    budget_balance = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    disbursement_date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.pk:
            original = Disbursement.objects.get(pk=self.pk)
            old_disbursement_amount = original.disbursement_amount
            new_disbursement_amount = self.disbursement_amount
            total_disbursement_amount = old_disbursement_amount + new_disbursement_amount
        else:
            total_disbursement_amount = self.disbursement_amount

        total_disbursement_amount = Decimal(total_disbursement_amount)

        total_disbursed = self.grant_account.disbursements.exclude(pk=self.pk).aggregate(
            total=models.Sum('disbursement_amount'))['total'] or Decimal('0')
        total_disbursed += total_disbursement_amount

        if total_disbursed > self.grant_account.budget_total.budget_total:
            raise ValidationError(
                "Total disbursement amount cannot exceed the budget total.")

        self.budget_balance = self.grant_account.budget_total.budget_total - \
            total_disbursement_amount
        self.disbursement_amount = total_disbursement_amount

        super().save(*args, **kwargs)

    def clean(self):
        if self.disbursement_amount > self.grant_account.budget_total.budget_total:
            raise ValidationError(
                "Disbursement amount cannot exceed the total budget.")

    def __str__(self):
        return f"Disbursement of {self.disbursement_amount} for {self.grant_account.account_holder} on {self.disbursement_date}"

    @classmethod
    def create_disbursement(cls, grant_account, amount):
        disbursement = cls(grant_account=grant_account,
                           disbursement_amount=Decimal(amount))
        disbursement.full_clean()
        disbursement.save()
        return disbursement


class GrantCloseOut(models.Model):
    REASON_CHOICES = (
        ('completed', 'Completed'),
        ('terminated', 'Terminated'),
        ('suspended', 'Suspended'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    grant_account = models.ForeignKey(
        'GrantAccount', on_delete=models.CASCADE, related_name='close_outs')
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='initiated_closeouts')
    initiated_date = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    completed_kpis = models.ForeignKey(
        'ProgressReport', on_delete=models.SET_NULL, null=True, blank=True)
    lessons_learnt = models.TextField(blank=True, null=True)
    best_practices = models.TextField(blank=True, null=True)
    achievements = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    blank=True, null=True, related_name='approved_closeouts')
    review_date = models.DateTimeField(blank=True, null=True)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"GrantCloseOut for {self.grant_account} initiated by {self.initiated_by}"


class GrantCloseOutDocuments(models.Model):
    closeout = models.ForeignKey(
        GrantCloseOut, on_delete=models.CASCADE, related_name='documents')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='closeout_documents')
    document = models.JSONField(default=dict)
    file = models.FileField(upload_to='closeout_documents/')  # Add this line
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for Closeout {self.closeout.grant_account}"


# class GrantCloseOutReview(models.Model):
#     closeout = models.ForeignKey(
#         GrantCloseOut, on_delete=models.CASCADE, related_name='reviews')
#     reviewer = models.ForeignKey(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
#     review_date = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=20, choices=[
#         ('approved', 'Approved'),
#         ('rejected', 'Rejected'),
#     ], default='pending')
#     comments = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return f"Review for Closeout {self.closeout.grant_account} by {self.reviewer}"

class Modifications(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    grant_account = models.ForeignKey(
        'GrantAccount', on_delete=models.CASCADE, related_name='modifications')
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requested_modifications')
    requested_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reviewed_modifications')
    review_date = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True, null=True)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"Modification for {self.grant_account} requested by {self.requested_by}"


class Requests(models.Model):
    REQUEST_TYPE_CHOICES = (
        ('modification', 'Modification'),
        ('requirements', 'Requirements'),
        ('grant_closeout', 'Grant Closeout'),
        ('extension', 'Extension'), 
    )
    request_type = models.CharField(
        max_length=50, choices=REQUEST_TYPE_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='requests')
    created_at = models.DateTimeField(auto_now_add=True)
    grant_closeout = models.ForeignKey(
        'GrantCloseOut', on_delete=models.SET_NULL, null=True, blank=True, related_name='requests')
    modifications = models.ForeignKey(
        'Modifications', on_delete=models.SET_NULL, null=True, blank=True, related_name='requests')
    requirements = models.ForeignKey(
        'Requirements', on_delete=models.SET_NULL, null=True, blank=True, related_name='requests')
    extensions = models.ForeignKey(
        'Extensions', on_delete=models.SET_NULL, null=True, blank=True, related_name='requests')
    reviewed = models.BooleanField(default=False)    
   

    def __str__(self):
        return f"{self.request_type} request for {self.request_type} by {self.user}"

    @property
    def status(self):
        if self.grant_closeout:
            return self.grant_closeout.status
        elif self.modifications:
            return self.modifications.status
        return 'N/A'

class Requirements(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    grant_account = models.ForeignKey(
        'GrantAccount', on_delete=models.CASCADE, related_name='requirements')
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requested_requirements')
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    items = models.JSONField()
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reviewed_requirements')
    reviewed = models.BooleanField(default=False)
    review_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Requirement for {self.grant_account} requested by {self.requested_by}"

    class Meta:
        verbose_name_plural = "Requirements"


class RequestReview(models.Model):
    REVIEW_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    request = models.OneToOneField(
        'Requests', on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    review_date = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=REVIEW_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f'Review for Request {self.request.id} by {self.reviewer}'


class Extensions(models.Model):
    REVIEW_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    grant_account = models.ForeignKey(
        'GrantAccount', on_delete=models.CASCADE, related_name='extensions')
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requested_extensions')
    request_date = models.DateTimeField(auto_now_add=True)
    extension_period = models.DurationField()
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reviewed_extensions')
    review_date = models.DateTimeField(null=True, blank=True)
    reviewed = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20, choices=REVIEW_STATUS_CHOICES, default='pending')
    reason = models.TextField(blank=True, null=True)    

    def __str__(self):
        return f"Extension for {self.grant_account} requested by {self.requested_by}"
