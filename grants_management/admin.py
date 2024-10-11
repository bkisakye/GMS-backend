from django.contrib import admin
from .models import (
    GrantType,
    Donor,
    SubgranteeCategory,
    GrantApplication,
    Grant,
    DefaultApplicationQuestion,
    SubSection,
    Section,
    GrantApplicationResponses,
    GrantApplicationReview,
    TransformedGrantApplicationData,
    GrantApplicationDocument,
    FilteredGrantApplicationResponse,
    GrantAccount,
    BudgetTotal,
    BudgetItem,
    BudgetCategory,
    FundingAllocation,
    FinancialReport,
    ProgressReport,
    Disbursement,
    GrantCloseOut,
    GrantCloseOutDocuments,
RequestReview,
    Modifications,
    Requests,
    Requirements,
    Extensions,
    GrantApplicationReviewDocument,
)


admin.site.register(Modifications)

admin.site.register(GrantCloseOutDocuments)

@admin.register(TransformedGrantApplicationData)
class TransformedGrantApplicationDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'grant')

@admin.register(Requirements)
class RequirementsAdmin(admin.ModelAdmin):
    list_display = ('grant_account', 'requested_by', 'request_date', 'items', 'reviewed', 'reviewed_by', 'status')

@admin.register(Requests)
class RequestsAdmin(admin.ModelAdmin):
    list_display = ('user', 'request_type','created_at', 'reviewed')

@admin.register(RequestReview)
class RequestReviewAdmin(admin.ModelAdmin):
    list_display = ('request', 'reviewer', 'review_date', 'status', 'comments')

@admin.register(GrantCloseOut)
class GrantCloseOutAdmin(admin.ModelAdmin):
    list_display = ('grant_account', 'initiated_by', 'reason', 'reviewed')

@admin.register(GrantApplicationReviewDocument)
class GrantApplicationReviewDocumentAdmin(admin.ModelAdmin):
    list_display = ('review', 'uploads')

@admin.register(GrantApplicationResponses)
class GrantApplicationResponsesAdmin(admin.ModelAdmin):
    list_display = ('grant', 'user', 'question', 'answer', 'choices')

@admin.register(GrantApplicationDocument)
class GrantApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ('application', 'user', 'uploaded_at', 'documents')

@admin.register(FundingAllocation)
class FundingAllocationAdmin(admin.ModelAdmin):
    list_display = ('grant_account', 'allocation_date', 'reference_number', 'item', 'description', 'amount', 'total_allocated')

@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    list_display = ('grant_account', 'report_date', 'fiscal_year', 'report_data', 'created_at', 'review_comments', 'review_status', 'reviewer')

@admin.register(FilteredGrantApplicationResponse)
class FilteredGrantApplicationResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'application', 'question', 'choices')

@admin.register(Extensions)
class ExtensionsAdmin(admin.ModelAdmin):
    list_display = ('grant_account', 'requested_by', 'extension_period', 'request_date', 'reviewed', 'reviewed_by')

@admin.register(BudgetCategory)
class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'description')
    search_fields = ('name', 'description')

@admin.register(Disbursement)
class DisbursementAdmin(admin.ModelAdmin):
    list_display = ('grant_account', 'disbursement_amount', 'disbursement_date', 'budget_balance')
    

@admin.register(BudgetItem)
class BudgetItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'grant_account', 'amount', 'category', 'fiscal_year', 'description')

@admin.register(ProgressReport)
class ProgressReportAdmin(admin.ModelAdmin):
    list_display = ("grant_account", "report_date",
                    "completed_pkis", "status", "progress_percentage")
    list_filter = ("grant_account", "report_date",
                   "completed_pkis", "status", "progress_percentage")


@admin.register(GrantAccount)
class GrantAccountAdmin(admin.ModelAdmin):
    list_display = ('budget_total', 'account_holder',
                    'current_amount', 'status')
    list_filter = ('grant', 'account_holder', 'status')
    search_fields = ('grant__name', 'account_holder')

    def budget_total(self, obj):
        # Replace this with the actual logic to calculate BudgetTotal
        return obj.calculate_budget_total()  # Ensure this method exists in GrantAccount

    budget_total.short_description = 'Budget Total'  # Label for the admin



@admin.register(BudgetTotal)
class BudgetTotalAdmin(admin.ModelAdmin):
    list_display = ("grant", "budget_total", "application", "user")


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(SubSection)
class SubSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'section')


@admin.register(GrantType)
class GrantTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "details", "is_active")
    search_fields = ("name", "details")
    list_filter = ("name", "details")


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ("name", "details", "is_active")
    search_fields = ("name", "details")
    list_filter = ("name", "details")


@admin.register(SubgranteeCategory)
class SubgranteeCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "details")
    search_fields = ("name", "details")
    list_filter = ("name", "details")


@admin.register(GrantApplication)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("grant", "subgrantee", "status",
                    "date_submitted", "signed", "reviewed", "updated",)
    list_filter = ("status", "date_submitted")
    search_fields = ("grant__name", "subgrantee__name")


@admin.register(Grant)
class GrantsAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "is_active",
        "start_date",
        "end_date",
        "category",
        "donor",
        "get_districts",
        "amount",
        "application_deadline",
        "eligibility_details",
        "reporting_time",
        "is_open",
        "created",
        "updated",
        "number_of_awards",
    )
    search_fields = ("name", "description")
    list_filter = ("name", "description")

    def get_districts(self, obj):
        return ", ".join(district.name for district in obj.district.all())
    get_districts.short_description = "Districts"


@admin.register(DefaultApplicationQuestion)
class DefaultApplicationQuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "question_type", "get_subsection", "get_section")
    search_fields = ("text", "question_type")

    def get_subsection(self, obj):
        return obj.sub_section.title if obj.sub_section else "None"

    get_subsection.short_description = "Subsection"

    def get_section(self, obj):
        return (
            obj.sub_section.section.title
            if obj.sub_section and obj.sub_section.section
            else "None"
        )

    get_section.short_description = "Section"


@admin.register(GrantApplicationReview)
class GrantApplicationReviewAdmin(admin.ModelAdmin):
    list_display = ("application", "reviewer", "status", "score", )
    list_filter = ("status",)
    search_fields = ("application", "reviewer__name",)


# Optionally, you can customize the admin site header and title
admin.site.site_header = "Grant Management System Admin"
admin.site.site_title = "Grant Management System Portal"
admin.site.index_title = "Welcome to the Grant Management System Administration"
