from django.contrib import admin
from subgrantees.models import (
    Contract,
    County,
    Region,
    ContractType,
    District,
    SubgranteeCategory,
    SubgranteeProfile,
    Subcounty
)


@admin.register(SubgranteeProfile)
class SubgranteeProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "district",
        
        "category",
    )
    search_fields = ("district", "contact_person")
    list_filter = ("district", "category")


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
