from django.urls import path
from .views import AuthenticateUser, LoginUserView, GranteeSignupView, AdminApprovalView, get_subgrantees_count, get_active_subgrantees_count, get_all_subgrantees, delete_subgrantee
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('authenticate/', AuthenticateUser.as_view(), name='api_authenticate'),
    path('register/', GranteeSignupView.as_view(), name='grantee_signup'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('admin/approve/', AdminApprovalView.as_view(), name='admin-approval'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('subgrantees/count/', get_subgrantees_count,
         name='get_subgrantees_count'),
    path('active-subgrantees/count/', get_active_subgrantees_count,
         name='get_active_subgrantees_count'),
    path('subgrantees/', get_all_subgrantees, name='get_all_subgrantees'),
    path('subgrantees/<int:user_id>/delete/',
         delete_subgrantee, name='delete_subgrantee'),
]
