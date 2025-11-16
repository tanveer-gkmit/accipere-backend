from django.contrib import admin
from .models import Jobs


@admin.register(Jobs)
class JobsAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'status', 'employment_type', 'created_at', 'deleted_at']
    list_filter = ['status', 'employment_type', 'experience_level', 'deleted_at']
    search_fields = ['title', 'description', 'department']
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    
    def get_queryset(self, request):
        # Show all objects including soft-deleted in admin
        return self.model.all_objects.get_queryset()
