
from django.urls import path
from .views import NotificationsListView, NotificationsCountView, MarkNotificationAsReadView, CreateNotificationView, UnreadNotificationsView, NotificationsAll, UserNotificationsView, NotificationReviewActionAPIView

urlpatterns = [
    path('notifications/', NotificationsListView.as_view(), name='notifications-list'),
    path('notifications/count/', NotificationsCountView.as_view(), name='notifications-count'),
    path('notifications/<int:pk>/read/', MarkNotificationAsReadView.as_view(), name='notification-mark-read'),
    path('notifications/create/', CreateNotificationView.as_view(), name='create-notification'),
    path('notifications/unread/', UnreadNotificationsView.as_view(),
         name='unread_notifications'),
    path('all-notifications/', NotificationsAll.as_view(), name='all-notifications'), 
    path('notifications/<int:user_id>/',  UserNotificationsView.as_view(), name='nots'),   
    path('notifications/<int:pk>/review-action/',
         NotificationReviewActionAPIView.as_view(), name='notification-review-action'),
]
