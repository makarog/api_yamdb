from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настроки администрационной модели кастомного пользователя."""
    list_display = ("pk", "username", "email", "bio",
                    "role", "confirmation_code", 'is_staff')

    @admin.display(description='role')
    def role(self, obj):
        return obj.role
