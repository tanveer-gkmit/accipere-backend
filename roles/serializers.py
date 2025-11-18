from rest_framework import serializers
from .models import Role


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model"""
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']
