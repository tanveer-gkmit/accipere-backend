from rest_framework import serializers
from .models import ApplicationStatuses

class ApplicationStatusesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationStatuses
        fields = ['id', 'name', 'description', 'order_sequence', 'created_at', 'updated_at']
        read_only_fields = ['order_sequence', 'created_at', 'updated_at']
