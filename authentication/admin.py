from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, UserProfile, LDAPUser, Activation, PasswordReset

class CustomUserAdmin(UserAdmin):
    # Define admin model for custom User model with no username field
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('fname', 'lname')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_approved', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'organisation_name', 'is_staff', 'is_active', 'is_approved')
    search_fields = ('email',)
    ordering = ('email',)

# Register your models here
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile)  # Add this line if you want UserProfile in the admin
admin.site.register(LDAPUser)  # Add this line if you want LDAPUser in the admin
admin.site.register(Activation)  # Add this line if you want Activation in the admin
admin.site.register(PasswordReset)  # Add this line if you want PasswordReset in the admin
