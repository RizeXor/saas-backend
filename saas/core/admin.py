from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import SubscriptionUser


class SubscriptionUserAdmin(BaseUserAdmin):
    list_display = ("email", "first_name", "last_name", "is_admin")
    list_filter = ("is_admin",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                    "first_name",
                    "last_name",
                    "is_admin",
                    "stripe_id",
                )
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)
    filter_horizontal = ()


admin.site.register(SubscriptionUser, SubscriptionUserAdmin)
admin.site.unregister(Group)
