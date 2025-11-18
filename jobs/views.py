from django.shortcuts import render
from .serializers import JobSerializer
from .models import Jobs
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from common.permissions import IsRecruiter, IsAdmin 
from rest_framework.permissions import AllowAny, IsAuthenticated
from applications.serializers import ApplicationListSerializer


class JobViewset(viewsets.ModelViewSet):
    queryset = Jobs.objects.all()
    serializer_class = JobSerializer
    
    def get_queryset(self):
        """
        Filter jobs based on authentication status.
        - Unauthenticated users: only see Open jobs
        - Authenticated users: see all jobs
        """
        if self.request.user.is_authenticated:
            return Jobs.objects.all()
        else:
            return Jobs.objects.filter(status='Open')
    
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
    
    def perform_create(self, serializer):
        """Automatically set posted_by_user_id to current user."""
        serializer.save(posted_by_user_id=self.request.user)
    
    def perform_destroy(self, instance):
        """Soft delete by default."""
        instance.delete()  # This will soft delete
    
    @action(detail=True, methods=['get'], url_path='applicants', permission_classes=[IsRecruiter])
    def applicants(self, request, pk=None):
        """Get all applicants for a specific job"""
        job = self.get_object()
        applications = job.applications.select_related('job_id', 'current_status').all()
        serializer = ApplicationListSerializer(applications, many=True)
        return Response(serializer.data)
