from rest_framework import serializers
from authentication.models import CustomUser
from subgrantees.models import (
    Contract,
    ContractType,
    District,
    SubgranteeCategory,
    SubgranteeProfile,
)


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id",  "email", "organisation_name", "phone_number"]


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ["id", "name"]


class SubgranteeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubgranteeCategory
        fields = ["id", "name"]


class ContractTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractType
        fields = "__all__"


class SubgranteeProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    category = SubgranteeCategorySerializer(read_only=True)

    class Meta:
        model = SubgranteeProfile
        fields = "__all__"

    def validate_district(self, value):
        if not District.objects.filter(id=value).exists():
            raise serializers.ValidationError("District not found.")
        return value

    def validate_category(self, value):
        if not SubgranteeCategory.objects.filter(id=value).exists():
            raise serializers.ValidationError("Category not found.")
        return value


class ContractSerializer(serializers.ModelSerializer):
    subgrantee = SubgranteeProfileSerializer(read_only=True)
    contract_type = ContractTypeSerializer(read_only=True)

    class Meta:
        model = Contract
        fields = [
            "id",
            "subgrantee",
            "application",
            "start_date",
            "end_date",
            "contract_type",
            "is_active",
        ]
