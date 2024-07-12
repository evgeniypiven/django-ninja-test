"""
Authorization admin
"""

# Standard library imports.

# Related third party imports.
from django.contrib import admin

# Local application/library specific imports.
from .models import CustomUser


class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'username', 'email', 'is_staff', 'is_active'
            )
        }),
    )


admin.site.register(CustomUser, UserAdmin)
