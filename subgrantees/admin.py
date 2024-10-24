from django.contrib import admin
from subgrantees.models import (
    Contract,
    County,
    Region,
    ContractType,
    District,
    SubgranteeCategory,
    SubgranteeProfile,
    Subcounty,
    Bank
)

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ("name", "head_office", "contact_info", "website", "year_of_establishment")
    search_fields = ("name", )
    list_filter = ("name",)

@admin.register(SubgranteeProfile)
class SubgranteeProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "acronym", "organisation_address", "registration_number")
    search_fields = ("user", "acronym",)
    


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("name", "region")
    search_fields = ("name",)
    list_filter = ("region",)


@admin.register(SubgranteeCategory)
class SubgranteeCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "details")
    search_fields = ("name",)


@admin.register(ContractType)
class ContractTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "details")
    search_fields = ("name",)



@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ("name", "district")
    search_fields = ("name",)
    list_filter = ("district",)


@admin.register(Subcounty)
class SubcountyAdmin(admin.ModelAdmin):
    list_display = ("name", "county")
    search_fields = ("name",)
    list_filter = ("county",)
