from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('get_users', 'notification_type', 'text',
                    'timestamp', 'is_read', 'notification_category', 'review_recommendation', 'status')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('text', 'user__email')

    def get_users(self, obj):
        return ", ".join(user.email for user in obj.user.all())
    get_users.short_description = 'Users'

    # Optionally, you can add additional configuration here
