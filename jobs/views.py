from django.shortcuts import render
from .serializers import JobSerializer
from .models import Jobs
from rest_framework import viewsets
from common.permissions import IsRecruiter, IsAdmin 
from rest_framework.permissions import AllowAny, IsAuthenticated


class JobViewset(viewsets.ModelViewSet):
    queryset = Jobs.objects.all()
    serializer_class = JobSerializer
    
    def get_permissions(self):
        """
        Set permissions based on action.
        """
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action in ['create', 'update', 'partial_update']:
            return [IsRecruiter()]
        elif self.action == 'destroy':
            return [IsAdmin()]
        return [IsAuthenticated()]
    
    def perform_destroy(self, instance):
        """Soft delete by default."""
        instance.delete()  # This will soft delete
