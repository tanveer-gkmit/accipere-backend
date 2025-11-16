from django.contrib import admin

# Register your models here.
from .models import (
    Applications,
    ApplicationStatuses,
    ApplicationAssignedUserStatuses
)


@admin.register(Applications)
class ApplicationsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "email",
        "phone_no",
        "job_id",
        "city",
        "created_at"
    )

    search_fields = (
        "first_name",
        "last_name",
        "email",
        "phone_no",
        "city",
    )

    list_filter = ("city", "created_at")

    def get_queryset(self, request):
        # Show all objects including soft-deleted in admin
        return self.model.all_objects.get_queryset()


@admin.register(ApplicationStatuses)
class ApplicationStatusesAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "order_sequence", "created_at")
    search_fields = ("name",)
    ordering = ("order_sequence",)


@admin.register(ApplicationAssignedUserStatuses)
class ApplicationAssignedUserStatusesAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "application_id",
        "status_id",
        "assigned_user_id",
        "created_at"
    )

    search_fields = (
        "application_id__first_name",
        "application_id__last_name",
        "assigned_user_id__username",
        "status_id__name",
    )

    list_filter = ("status_id", "created_at")

    def get_queryset(self, request):
        # Show all objects including soft-deleted in admin
        return self.model.all_objects.get_queryset()