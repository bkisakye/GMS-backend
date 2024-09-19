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

admin.site.register(GrantApplicationReviewDocument)

admin.site.register(Extensions)

admin.site.register(Requirements)

admin.site.register(Requests)

admin.site.register(Modifications)

admin.site.register(RequestReview)

admin.site.register(GrantCloseOutDocuments)

admin.site.register(GrantCloseOut)

admin.site.register(Disbursement)

admin.site.register(FinancialReport)

admin.site.register(FundingAllocation)

admin.site.register(BudgetCategory)

admin.site.register(BudgetItem)

admin.site.register(GrantApplicationResponses)

admin.site.register(TransformedGrantApplicationData)

admin.site.register(GrantApplicationDocument)

admin.site.register(FilteredGrantApplicationResponse)


@admin.register(ProgressReport)
class ProgressReportAdmin(admin.ModelAdmin):
    list_display = ("grant_account", "report_date",
                    "completed_pkis", "status", "progress_percentage")
    list_filter = ("grant_account", "report_date",
                   "completed_pkis", "status", "progress_percentage")


@admin.register(GrantAccount)
class GrantAccountAdmin(admin.ModelAdmin):
    list_display = ('grant', 'account_holder', 'budget_total',
                    'current_amount', 'status')
    list_filter = ('grant', 'account_holder', 'status')
    search_fields = ('grant__name', 'account_holder')


@admin.register(BudgetTotal)
class BudgetTotalAdmin(admin.ModelAdmin):
    list_display = ("grant", "budget_total")


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(SubSection)
class SubSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'section')


@admin.register(GrantType)
class GrantTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "details")
    search_fields = ("name", "details")
    list_filter = ("name", "details")


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ("name", "details")
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
                    "date_submitted", "signed", "reviewed", )
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
