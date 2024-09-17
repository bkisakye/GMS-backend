from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.conf import settings
from rest_framework import viewsets
from .models import (SubgranteeProfile, District, SubgranteeCategory
                     )
from authentication.models import CustomUser
from .serializers import (
    SubgranteeProfileSerializer,
    DistrictSerializer,
)
from grants_management.serializers import GrantTypeSerializer
from rest_framework.decorators import api_view
import json
import os
import logging
from django.http import JsonResponse
from utilities.helpers import check_request_data
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import permissions, status
from grants_management.models import GrantType

logger = logging.getLogger(__name__)


class SubgranteeProfileCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"status": "error", "message": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            # Fetch the profile for the authenticated user
            profile = SubgranteeProfile.objects.get(user=request.user)
        except SubgranteeProfile.DoesNotExist:
            return Response(
                {"status": "error", "message": "Profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        updatable_fields = [
            "organisation_address",
            "contact_person",
            "secondary_contact",
            "acronym",
            "website",
            "executive_director_name",
            "executive_director_contact",
            "board_chair_name",
            "board_chair_contact",
            "created_date",
            "most_recent_registration_date",
            "registration_number",
            "has_mission_vision_values",
            "mission",
            "vision",
            "core_values",
            "role_on_board",
            "meeting_frequency_of_board",
            "last_three_meetings_of_board",
            "organization_description",
            "organization_programmatic_capacity",
            "organization_financial_management_capacity",
            "organization_administrative_management_capacity",
            "accounting_system",
            "finance_and_admin_dtl_finance_admin_manual_updated_date",
            "finance_and_admin_dtl_finance_admin_manual",
            "finance_and_admin_dtl_finance_admin_manual_reason",
            "finance_and_admin_dtl_hr_manual",
            "finance_and_admin_dtl_hr_manual_updated_date",
            "finance_and_admin_dtl_hr_manual_reason",
            "finance_and_admin_dtl_anti_corruption_policy",
            "finance_and_admin_dtl_audits_in_last_three_years",
            "finance_and_admin_dtl_audit_details",
            "finance_and_admin_dtl_audit_details_not",
            "finance_and_admin_dtl_audit_issues_and_actions",
            "finance_and_admin_dtl_forensic_audit",
            "finance_and_admin_dtl_forensic_audit_details",
            "audit_date",
            "audit_issue_raised",
            "audit_action_taken",
            "audit_name",
            "technical_skills",
            "technical_skills_comparative_advantage",
            "technical_skills_monitoring_and_evaluation_capacity",
            "technical_skills_impact_determination",
            "technical_skills_external_evaluation_conducted",
            "technical_skills_external_evaluation_details",
            "technical_skills_external_evaluation_details_not",
            "technical_skills_evaluation_use",
            "staff_male",
            "staff_female",
            "volunteers_male",
            "volunteers_female",
            "staff_dedicated_to_me",
            "me_responsibilities",
            "me_coverage",
            "gender_inclusion",
            "finance_manager",
            "finance_manager_details",
            "past_projects",
            "current_projects",
            "current_work_emphasizes",
            "partnerships",
            "subgrants",
        ]

        for field in updatable_fields:
            if field in request.data:
                # Handle foreign key fields separately
                if field in ['district', 'category']:
                    fk_id = request.data[field].get('id') if isinstance(
                        request.data[field], dict) else request.data[field]
                    if fk_id:
                        if field == 'district':
                            setattr(profile, field, get_object_or_404(
                                District, id=fk_id))
                        elif field == 'category':
                            setattr(profile, field, get_object_or_404(
                                GrantType, id=fk_id))
                else:
                    setattr(profile, field, request.data[field])

        try:
            profile.save()
            return Response(
                {
                    "status": "success",
                    "message": "Profile updated successfully.",
                    "profile": SubgranteeProfileSerializer(profile).data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": f"Error updating profile: {str(e)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


@api_view(["GET"])
def check_user_profile(request, user_id):
    try:

        user = CustomUser.objects.get(id=user_id)
        profile = SubgranteeProfile.objects.get(user=user)
        if profile.is_completed:
            return Response({"has_profile": True}, status=status.HTTP_200_OK)
        else:
            return Response({"has_profile": False}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except SubgranteeProfile.DoesNotExist:
        return Response({"has_profile": False}, status=status.HTTP_200_OK)


class SubgranteeProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = SubgranteeProfile.objects.all()
    serializer_class = SubgranteeProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        user = self.request.user
        if not user.is_authenticated:
            raise ValidationError(
                "User must be authenticated to update a profile.")

        district_id = self.request.data.get("district")
        category_id = self.request.data.get("category")

        try:
            district = District.objects.get(id=district_id)
        except District.DoesNotExist:
            raise ValidationError(
                f"District with id {district_id} does not exist.")

        try:
            category = SubgranteeCategory.objects.get(id=category_id)
        except SubgranteeCategory.DoesNotExist:
            raise ValidationError(
                f"Category with id {category_id} does not exist.")

        serializer.save(user=user, district=district, category=category)


class SubgranteeProfileMeView(generics.RetrieveUpdateAPIView):
    serializer_class = SubgranteeProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        try:
            return SubgranteeProfile.objects.get(user=user)
        except SubgranteeProfile.DoesNotExist:
            raise NotFound("Profile for the current user does not exist.")

    def perform_update(self, serializer):
        user = self.request.user
        district_id = self.request.data.get("district")
        category_id = self.request.data.get("category")

        if district_id:
            try:
                district = District.objects.get(id=district_id)
            except District.DoesNotExist:
                raise ValidationError(
                    f"District with id {district_id} does not exist.")
            serializer.validated_data["district"] = district

        if category_id:
            try:
                category = SubgranteeCategory.objects.get(id=category_id)
            except SubgranteeCategory.DoesNotExist:
                raise ValidationError(
                    f"Category with id {category_id} does not exist.")
            serializer.validated_data["category"] = category

        serializer.save(user=user)


class DistrictListView(generics.ListAPIView):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [permissions.IsAuthenticated]


def districts(request):
    if request.method == "GET":
        json_file_path = os.path.join(settings.BASE_DIR, "districts.json")
        with open(json_file_path, "r") as file:
            data = json.load(file)
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def get_all_profiles(request):
    profiles = SubgranteeProfile.objects.all()
    serializer = SubgranteeProfileSerializer(profiles, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
