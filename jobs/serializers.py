from rest_framework import serializers
from .models import Jobs


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jobs
        fields = "__all__"
        read_only_fields = ['id', 'posted_by_user_id', 'posted_date', 'created_at', 'updated_at']