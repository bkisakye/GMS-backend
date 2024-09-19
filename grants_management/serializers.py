from .models import BudgetItem, GrantAccount, BudgetCategory
from rest_framework import serializers
from grants_management.models import (
    Donor,
    Grant,
    GrantApplication,
    Requirements,
    GrantApplicationReview,
    GrantType,
    DefaultApplicationQuestion,
    GrantApplicationResponses,
    Section,
    SubSection,
    GrantApplicationDocument,
    TransformedGrantApplicationData,
    FilteredGrantApplicationResponse,
    FundingAllocation,
    BudgetItem,
    GrantAccount,
    BudgetCategory,
    BudgetTotal,
    ProgressReport,
    Disbursement,
    GrantCloseOut,
    GrantCloseOutDocuments,
    RequestReview,
    Modifications,
    Requests,
    Extensions,
    FinancialReport,
    GrantApplicationReviewDocument,

)
from authentication.models import CustomUser
from authentication.serializers import CustomUserSerializer
from subgrantees.models import SubgranteeCategory, District
from subgrantees.serializers import CustomUserSerializer, SubgranteeProfileSerializer, DistrictSerializer
from django.contrib.auth import get_user_model


class GrantTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrantType
        fields = "__all__"


class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = "__all__"


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ["id", "title"]


class SubSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubSection
        fields = ["id", "title", "section"]


class BudgetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetCategory
        fields = ['id', 'name', 'description', 'user']


class GrantSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=GrantType.objects.all(),
        write_only=True,
    )
    donor = serializers.PrimaryKeyRelatedField(
        queryset=Donor.objects.all(),
        allow_null=True,
        required=False,
        write_only=True,
    )
    district = serializers.PrimaryKeyRelatedField(
        queryset=District.objects.all(),
        many=True,
        write_only=True,
    )

    category_detail = GrantTypeSerializer(read_only=True, source='category')
    donor_detail = DonorSerializer(read_only=True, source='donor')
    specific_questions = serializers.SerializerMethodField()
    district_detail = DistrictSerializer(read_only=True, many=True)

    class Meta:
        model = Grant
        fields = [
            "id",
            "name",
            "description",
            "start_date",
            "end_date",
            "amount",
            "is_open",
            "category",
            "category_detail",
            "donor",
            "donor_detail",
            "specific_questions",
            "application_deadline",
            "eligibility_details",
            "district",
            "district_detail",
            "kpis",
            "reporting_time",
            "created",
            "updated",
            "number_of_awards",
        ]

    def validate(self, data):
        if data.get("start_date") and data.get("end_date"):
            if data["start_date"] > data["end_date"]:
                raise serializers.ValidationError(
                    "End date must be after start date.")
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category_detail'] = GrantTypeSerializer(
            instance.category).data
        if instance.donor:
            representation['donor_detail'] = DonorSerializer(
                instance.donor).data
        representation['district_detail'] = DistrictSerializer(
            instance.district.all(), many=True).data
        return representation

    def get_specific_questions(self, obj):
        questions = DefaultApplicationQuestion.objects.filter(grant=obj)
        return DefaultApplicationQuestionSerializer(questions, many=True).data

    def create(self, validated_data):
        districts = validated_data.pop('district', [])
        grant = super().create(validated_data)
        if districts:
            grant.district.set(districts)
        return grant

    def update(self, instance, validated_data):
        districts = validated_data.pop('district', [])
        instance = super().update(instance, validated_data)
        if districts:
            instance.district.set(districts)
        return instance



class BudgetTotalSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetTotal
        fields = ['id', 'budget_total']


class GrantAccountSerializer(serializers.ModelSerializer):
    grant = GrantSerializer(read_only=True)
    account_holder = CustomUserSerializer(read_only=True)
    budget_total = BudgetTotalSerializer(read_only=True)

    class Meta:
        model = GrantAccount
        fields = ['id', 'grant', 'account_holder',
                  'budget_total', 'current_amount', 'disbursed', 'status']





class BudgetItemSerializer(serializers.ModelSerializer):
    grant_account = serializers.PrimaryKeyRelatedField(
        queryset=GrantAccount.objects.all())
    category = serializers.PrimaryKeyRelatedField(
        queryset=BudgetCategory.objects.all())

    class Meta:
        model = BudgetItem
        fields = ['id', 'category', 'user', 'grant_account',
                  'amount', 'description']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # This part serializes the related fields using nested serializers
        representation['grant_account'] = GrantAccountSerializer(
            instance.grant_account).data
        representation['category'] = BudgetCategorySerializer(
            instance.category).data
        return representation

    grant_account = serializers.PrimaryKeyRelatedField(
        queryset=GrantAccount.objects.all())
    category = serializers.PrimaryKeyRelatedField(
        queryset=BudgetCategory.objects.all())

    class Meta:
        model = BudgetItem
        fields = ['id', 'category', 'user', 'grant_account',
                  'amount', 'description', 'fiscal_year']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['grant_account'] = GrantAccountSerializer(
            instance.grant_account).data
        representation['category'] = BudgetCategorySerializer(
            instance.category).data
        return representation


class FundingAllocationSerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(
        queryset=BudgetItem.objects.all())

    class Meta:
        model = FundingAllocation
        fields = ['id', 'user', 'amount', 'allocation_date',
                  'description', 'item', 'reference_number']
        read_only_fields = ['reference_number', 'grant_account']

    def create(self, validated_data):
        item = validated_data['item']
        validated_data['grant_account'] = item.grant_account
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'item' in validated_data:
            instance.grant_account = validated_data['item'].grant_account
        return super().update(instance, validated_data)

class DefaultApplicationQuestionSerializer(serializers.ModelSerializer):
    section = SectionSerializer(read_only=True)
    sub_section = SubSectionSerializer(read_only=True)
    grant = GrantSerializer(read_only=True)

    class Meta:
        model = DefaultApplicationQuestion
        fields = "__all__"


class GrantApplicationSerializer(serializers.ModelSerializer):
    subgrantee = CustomUserSerializer(read_only=True)
    grant = GrantSerializer(read_only=True)

    class Meta:
        model = GrantApplication
        fields = "__all__"


class GrantApplicationReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrantApplicationReview
        fields = ['score', 'status', 'comments', 'application', 'reviewer', 'id']


    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            print("Setting reviewer:", request.user)  # Debug print
            validated_data['reviewer'] = request.user
        return super().create(validated_data)

    def validate(self, data):
        print("Validated data:", data)  # Add this line to debug
        return super().validate(data)


class FilteredGrantApplicationResponseSerializer(serializers.ModelSerializer):
    application_id = serializers.IntegerField(source='application.id')
    grant_id = serializers.IntegerField(source='application.grant.id')

    class Meta:
        model = FilteredGrantApplicationResponse
        fields = ['application_id', 'grant_id', 'question', 'choices']


class GrantApplicationResponsesSerializer(serializers.ModelSerializer):
    question = DefaultApplicationQuestionSerializer(read_only=True)
    grant = serializers.SerializerMethodField()

    class Meta:
        model = GrantApplicationResponses
        fields = ["id", "question", "answer", "choices", "grant", "user"]

    def get_grant(self, obj):
        return obj.question.grant.id if obj.question.grant else None


class GrantApplicationDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrantApplicationDocument
        fields = ['application', 'user', 'documents', 'uploaded_at']

class GrantApplicationReviewDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrantApplicationReviewDocument
        fields = ['review', 'uploads']

class TransformedGrantApplicationDataSerializer(serializers.Serializer):
    user = CustomUserSerializer(read_only=True)
    grant = GrantSerializer(read_only=True)
    transformed_data = serializers.JSONField()

    class Meta:
        model = TransformedGrantApplicationData
        fields = ['user', 'grant', 'transformed_data']


class ProgressReportSerializer(serializers.ModelSerializer):
    grant_account = GrantAccountSerializer(read_only=True)
    reviewer = CustomUserSerializer(read_only=True)

    class Meta:
        model = ProgressReport
        fields = ['id', 'grant_account', 'report_date',
                  'completed_pkis', 'status', 'progress_percentage', 'review_status', 'review_comments', 'reviewer', 'last_updated']
        read_only_fields = ['id', 'report_date',
                            'status', 'progress_percentage', 'review_status', 'last_updated']

class FinancialReportSerializer(serializers.ModelSerializer):
   grant_account = GrantAccountSerializer(read_only=True)

   class Meta:
       model = FinancialReport
       fields = "__all__"                             


class DisbursementSerializer(serializers.ModelSerializer):
    grant_account = GrantAccountSerializer(read_only=True)
    grant_account_id = serializers.PrimaryKeyRelatedField(
        queryset=GrantAccount.objects.all(),
        source='grant_account',
        write_only=True
    )

    class Meta:
        model = Disbursement
        fields = ['id', 'grant_account', 'grant_account_id',
                  'disbursement_amount', 'budget_balance', 'disbursement_date']
        read_only_fields = ['id', 'budget_balance', 'disbursement_date']

    def create(self, validated_data):
        return Disbursement.create_disbursement(
            grant_account=validated_data['grant_account'],
            amount=validated_data['disbursement_amount']
        )


class GrantCloseOutSerializer(serializers.ModelSerializer):
    grant_account = serializers.PrimaryKeyRelatedField(
        queryset=GrantAccount.objects.all(),
        required=False
    )
    completed_kpis = serializers.SerializerMethodField()
    initiated_by = CustomUserSerializer(read_only=True)
    reviewed_by = CustomUserSerializer(read_only=True)

    class Meta:
        model = GrantCloseOut
        fields = "__all__"

    def get_completed_kpis(self, obj):
        if obj.completed_kpis:
            return ProgressReportSerializer(obj.completed_kpis).data
        return None

    def validate(self, data):
        grant_account = data.get('grant_account')
        if grant_account is None:
            raise serializers.ValidationError(
                "The 'grant_account' field is required.")
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['initiated_by'] = request.user
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['grant_account'] = GrantAccountSerializer(
            instance.grant_account).data
        return representation


class GrantCloseOutDocumentsSerializer(serializers.ModelSerializer):
    closeout = GrantCloseOutSerializer(read_only=True)
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = GrantCloseOutDocuments
        fields = ['id', 'closeout', 'user', 'document', 'uploaded_at']
        read_only_fields = ['uploaded_at']


# class GrantCloseOutReviewSerializer(serializers.ModelSerializer):
#     closeout = serializers.PrimaryKeyRelatedField(
#         queryset=GrantCloseOut.objects.all(),
#         required=False
#     )
#     reviewer = serializers.PrimaryKeyRelatedField(
#         queryset=get_user_model().objects.all(),
#         required=False
#     )

#     class Meta:
#         model = GrantCloseOutReview
#         fields = "__all__"

class RequestReviewSerializer(serializers.ModelSerializer):
    request = serializers.PrimaryKeyRelatedField(
        queryset=Requests.objects.all(),
        required=False
    )
    
    reviewer = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        required=False
    )

    class Meta:
        model = RequestReview
        fields = "__all__"

class ModificationsSerializer(serializers.ModelSerializer):
    grant_account = serializers.PrimaryKeyRelatedField(
        queryset=GrantAccount.objects.all(),
        required=False
    )
    requested_by = CustomUserSerializer(read_only=True)
    reviewed_by = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        required=False
    )

    class Meta:
        model = Modifications
        fields = "__all__"

    def validate(self, data):
        grant_account = data.get('grant_account')
        grant_account_id = self.initial_data.get('grant_account_id')

        if not grant_account and not grant_account_id:
            raise serializers.ValidationError(
                "Either 'grant_account' or 'grant_account_id' must be provided.")

        if not grant_account and grant_account_id:
            try:
                data['grant_account'] = GrantAccount.objects.get(
                    id=grant_account_id)
            except GrantAccount.DoesNotExist:
                raise serializers.ValidationError(
                    f"GrantAccount with id {grant_account_id} does not exist.")

        return data

    def create(self, validated_data):
        requested_by = validated_data.pop('requested_by', None)
        if not requested_by:
            requested_by = self.context['request'].user
        validated_data['requested_by'] = requested_by
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['grant_account'] = GrantAccountSerializer(
            instance.grant_account).data
        return representation

class RequirementsSerializer(serializers.ModelSerializer):
    grant_account = serializers.PrimaryKeyRelatedField(
        queryset=GrantAccount.objects.all(),
        required=False
    )
    requested_by = CustomUserSerializer(read_only=True)

    class Meta:
        model = Requirements
        fields = "__all__"


    def validate(self, data):
        grant_account = data.get('grant_account')
        grant_account_id = self.initial_data.get('grant_account_id')

        if not grant_account and not grant_account_id:
            raise serializers.ValidationError(
                "Either 'grant_account' or 'grant_account_id' must be provided.")

        if not grant_account and grant_account_id:
            try:
                data['grant_account'] = GrantAccount.objects.get(
                    id=grant_account_id)
            except GrantAccount.DoesNotExist:
                raise serializers.ValidationError(
                    f"GrantAccount with id {grant_account_id} does not exist.")

        return data

    def create(self, validated_data):
        requested_by = validated_data.pop('requested_by', None)
        if not requested_by:
            requested_by = self.context['request'].user
        validated_data['requested_by'] = requested_by
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['grant_account'] = GrantAccountSerializer(
            instance.grant_account).data
        return representation


class ExtensionSerializer(serializers.ModelSerializer):
    request = serializers.PrimaryKeyRelatedField(
        queryset=Requests.objects.all(),
        required=False
    )
    reviewer = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        required=False
    )
    requested_by = CustomUserSerializer(read_only=True)

    class Meta:
        model = Extensions
        fields = "__all__"

    def validate(self, data):
        grant_account = data.get('grant_account')
        grant_account_id = self.initial_data.get('grant_account_id')

        if not grant_account and not grant_account_id:
            raise serializers.ValidationError(
                "Either 'grant_account' or 'grant_account_id' must be provided.")

        if not grant_account and grant_account_id:
            try:
                data['grant_account'] = GrantAccount.objects.get(
                    id=grant_account_id)
            except GrantAccount.DoesNotExist:
                raise serializers.ValidationError(
                    f"GrantAccount with id {grant_account_id} does not exist.")

        return data

    def create(self, validated_data):
        requested_by = validated_data.pop('requested_by', None)
        if not requested_by:
            requested_by = self.context['request'].user
        validated_data['requested_by'] = requested_by
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['grant_account'] = GrantAccountSerializer(
            instance.grant_account).data
        return representation

class RequestsSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    grant_closeout = GrantCloseOutSerializer(read_only=True)
    modifications = ModificationsSerializer(read_only=True)
    requirements = RequirementsSerializer(read_only=True)
    extensions = ExtensionSerializer(read_only=True)

    class Meta:
        model = Requests
        fields = "__all__"


