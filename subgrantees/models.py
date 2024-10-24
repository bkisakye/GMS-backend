from django.db import models
from django.conf import settings
from datetime import date
import logging
from django.utils import timezone


logger = logging.getLogger(__name__)


class Region(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class District(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class County(models.Model):
    name = models.CharField(max_length=255)
    district = models.ForeignKey(
        District, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Bank(models.Model):
    name = models.CharField(max_length=255)
    head_office = models.CharField(max_length=255)
    website = models.URLField()
    year_of_establishment = models.IntegerField()
    # This can store structured data as in your JSON
    contact_info = models.JSONField()

    def __str__(self):
        return self.name

class Subcounty(models.Model):
    name = models.CharField(max_length=255)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class SubgranteeCategory(models.Model):
    name = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class SubgranteeProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subgrantee_profile"
    )
    organisation_address = models.TextField(null=True, blank=True)
    contact_person = models.CharField(max_length=255, null=True, blank=True)
    secondary_contact = models.CharField(max_length=255, blank=True, null=True)
    district = models.ForeignKey(
        District,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subgrantee_profiles",
    )
    category = models.ForeignKey(
        'grants_management.GrantType', on_delete=models.CASCADE, null=True)
    acronym = models.CharField(max_length=40, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    executive_director_name = models.CharField(
        max_length=255, null=True, blank=True)
    executive_director_contact = models.CharField(
        max_length=255, null=True, blank=True)
    board_chair_name = models.CharField(max_length=255, null=True, blank=True)
    board_chair_contact = models.CharField(
        max_length=255, null=True, blank=True)
    created_date = models.DateField(default=timezone.now)
    most_recent_registration_date = models.DateField(default=timezone.now)
    registration_number = models.CharField(
        max_length=100, null=True, blank=True)
    has_mission_vision_values = models.BooleanField(default=False)
    mission = models.TextField(blank=True, null=True)
    vision = models.TextField(blank=True, null=True)
    core_values = models.TextField(blank=True, null=True)
    role_on_board = models.TextField(blank=True, null=True)
    meeting_frequency_of_board = models.CharField(
        max_length=255, null=True, blank=True)
    last_three_meetings_of_board = models.TextField(blank=True, null=True)
    organization_description = models.TextField(blank=True, null=True)
    organization_programmatic_capacity = models.TextField(
        blank=True, null=True)
    organization_financial_management_capacity = models.TextField(
        blank=True, null=True)
    organization_administrative_management_capacity = models.TextField(
        blank=True, null=True
    )
    accounting_system = models.CharField(max_length=255, null=True, blank=True)
    finance_and_admin_dtl_finance_admin_manual_updated_date = models.DateField(
        null=True, blank=True)
    finance_and_admin_dtl_finance_admin_manual = models.BooleanField(
        default=False)
    finance_and_admin_dtl_finance_admin_manual_reason = models.TextField(
        blank=True, null=True)
    finance_and_admin_dtl_hr_manual = models.BooleanField(default=False)
    finance_and_admin_dtl_hr_manual_updated_date = models.DateField(
        null=True, blank=True)
    finance_and_admin_dtl_hr_manual_reason = models.TextField(
        blank=True, null=True)
    finance_and_admin_dtl_anti_corruption_policy = models.BooleanField(
        default=False)
    finance_and_admin_dtl_audits_in_last_three_years = models.BooleanField(
        default=False)
    finance_and_admin_dtl_audit_details = models.TextField(
        blank=True, null=True)
    finance_and_admin_dtl_audit_details_not = models.TextField(
        blank=True, null=True)
    finance_and_admin_dtl_audit_issues_and_actions = models.TextField(
        blank=True, null=True
    )
    finance_and_admin_dtl_forensic_audit = models.BooleanField(default=False)
    finance_and_admin_dtl_forensic_audit_details = models.TextField(
        blank=True, null=True)
    audit_date = models.DateField(default=date.today)
    audit_issue_raised = models.TextField(null=True, blank=True)
    audit_action_taken = models.TextField(null=True, blank=True)
    audit_name = models.CharField(max_length=255, blank=True, null=True)
    technical_skills = models.TextField(blank=True, null=True)
    technical_skills_comparative_advantage = models.TextField(
        blank=True, null=True)
    technical_skills_monitoring_and_evaluation_capacity = models.TextField(
        blank=True, null=True)
    technical_skills_impact_determination = models.TextField(
        blank=True, null=True)
    technical_skills_external_evaluation_conducted = models.BooleanField(
        default=False)
    technical_skills_external_evaluation_details = models.TextField(
        blank=True, null=True)
    technical_skills_external_evaluation_details_not = models.TextField(
        blank=True, null=True)
    technical_skills_evaluation_use = models.TextField(blank=True, null=True)
    staff_male = models.PositiveIntegerField(blank=True, null=True)
    staff_female = models.PositiveIntegerField(blank=True, null=True)
    volunteers_male = models.PositiveIntegerField(blank=True, null=True)
    volunteers_female = models.PositiveIntegerField(blank=True, null=True)
    staff_dedicated_to_me = models.BooleanField(default=False)
    me_responsibilities = models.TextField(blank=True, null=True)
    me_coverage = models.TextField(blank=True, null=True)
    gender_inclusion = models.TextField(blank=True, null=True)
    finance_manager = models.BooleanField(default=False)
    finance_manager_details = models.TextField(blank=True, null=True)
    past_projects = models.JSONField(null=True, blank=True)
    current_projects = models.JSONField(null=True, blank=True)
    current_work_emphasizes = models.TextField(null=True, blank=True)
    partnerships = models.JSONField(null=True, blank=True)
    subgrants = models.JSONField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.organisation_name


class ContractType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Contract(models.Model):
    subgrantee = models.ForeignKey(
        SubgranteeProfile, on_delete=models.CASCADE, related_name="contracts"
    )
    application = models.ForeignKey(
        "grants_management.GrantApplication",
        on_delete=models.CASCADE,
        related_name="contracts",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    contract_type = models.ForeignKey(
        ContractType, on_delete=models.CASCADE, related_name="contracts"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Contract with {self.subgrantee} for {self.application}"
