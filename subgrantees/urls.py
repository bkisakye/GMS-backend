from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    districts,
    SubgranteeProfileCreateView,
    SubgranteeProfileDetailView,
    SubgranteeProfileMeView,
    check_user_profile,
    get_all_profiles,
)



urlpatterns = [
    path("districts/", districts, name="districts"),
    path(
        "profiles/",
        SubgranteeProfileCreateView.as_view(),
        name="subgrantee-profile-create",
    ),
    path(
        "profiles/<int:pk>/",
        SubgranteeProfileDetailView.as_view(),
        name="subgrantee-profile-detail",
    ),
    path(
        "profiles/me/", SubgranteeProfileMeView.as_view(), name="subgrantee-profile-me"
    ),
    path("check-profile/<int:user_id>/", check_user_profile, name="check_user_profile"),
    path('subgrantee-profiles/', get_all_profiles, name='get_all_profiles'),
]
