from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from common.permissions import IsRecruiter, IsAdmin 
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import ApplicationStatuses, Applications, ApplicationAssignedUserStatuses
from .serializers import (
    ApplicationStatusSerializer,
    ApplicationListSerializer,
    ApplicationDetailSerializer,
    ApplicationCreateSerializer,
    ApplicationUpdateSerializer
)


class ApplicationStatusesViewSet(viewsets.ModelViewSet):
    queryset = ApplicationStatuses.objects.all()
    serializer_class = ApplicationStatusSerializer

    def get_permissions(self):
        """
        Set permissions based on action.
        """
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action in ['create', 'update', 'partial_update','destroy','reorder']:
            return [IsAdmin()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['post'], url_path='reorder')
    def reorder(self, request):
        """
        Expects JSON payload:
        {
            "items": [
                {"id": "uuid-string-1", "order_sequence": 0},
                {"id": "uuid-string-2", "order_sequence": 1},
                {"id": "uuid-string-3", "order_sequence": 2}
            ]
        }
        """
        items = request.data.get('items', [])
        
        if not items:
            return Response(
                {'error': 'No items provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get IDs being updated
        updating_ids = [item['id'] for item in items]
        new_order_sequences = [item['order_sequence'] for item in items]
        
        # Check if any of the new order_sequence values already exist in statuses NOT being updated
        existing_conflicts = ApplicationStatuses.objects.filter(
            order_sequence__in=new_order_sequences
        ).exclude(id__in=updating_ids)
        
        if existing_conflicts.exists():
            return Response(
                {'error': 'Order sequence conflict with existing statuses'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # First pass: Set to negative values
                for idx, item in enumerate(items):
                    ApplicationStatuses.objects.filter(
                        id=item['id']
                    ).update(order_sequence=-(idx + 1))
                
                # Second pass: Set to final values
                for item in items:
                    ApplicationStatuses.objects.filter(
                        id=item['id']
                    ).update(order_sequence=item['order_sequence'])
            
            return Response({'message': 'Order updated successfully'})
        except Exception as e:
            return Response(
                {'error': 'Failed to update order'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Applications with soft delete support.
    Automatically creates ApplicationAssignedUserStatuses on creation.
    
    Permissions:
    - create: AllowAny (for public job applications)
    - list, retrieve, update, partial_update, destroy: IsRecruiter
    """
    queryset = Applications.objects.select_related(
        'job_id',
        'current_status'
    ).prefetch_related('status_history')
    
    def get_serializer_class(self):
        """
        Return different serializers based on action.
        """
        if self.action == 'list':
            return ApplicationListSerializer
        elif self.action == 'create':
            return ApplicationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ApplicationUpdateSerializer
        return ApplicationDetailSerializer
    
    def get_permissions(self):
        """
        Set permissions based on action.
        - create: AllowAny (public can apply)
        - all other actions: IsRecruiter
        """
        if self.action == 'create':
            return [AllowAny()]
        return [IsRecruiter()]
    
    @transaction.atomic
    def perform_create(self, serializer):
        """
        Override to create ApplicationAssignedUserStatuses alongside Application.
        """
        # Get status_notes from validated data before saving
        status_notes = serializer.validated_data.get('status_notes', '')
        
        # Save the application instance
        application = serializer.save()
        
        # Get the initial status (first in order_sequence)
        initial_status = ApplicationStatuses.objects.order_by('order_sequence').first()
        
        # Update the current_status on application
        if initial_status:
            application.current_status = initial_status
            application.save()
            
            # Create the status history entry
            # For public applications, assigned_user_id can be None
            assigned_user = self.request.user if self.request.user.is_authenticated else None
            
            ApplicationAssignedUserStatuses.objects.create(
                application_id=application,
                status_id=initial_status,
                assigned_user_id=assigned_user,
                notes=status_notes or f"Application created"
            )
    
    @transaction.atomic
    def perform_update(self, serializer):
        """
        Override to track status changes and update notes in ApplicationAssignedUserStatuses.
        Validates that status can only move forward (increasing order_sequence).
        """
        instance = self.get_object()
        old_status = instance.current_status
        
        # Get status_notes and new_status from validated data before save
        status_notes = serializer.validated_data.get('status_notes', '')
        new_status = serializer.validated_data.get('current_status')
        
        # If status is being changed, validate order_sequence progression
        if new_status and new_status != old_status:
            if old_status and new_status.order_sequence <= old_status.order_sequence:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({
                    'current_status': f'Status can only move forward. Current status order: {old_status.order_sequence}, '
                                     f'attempted status order: {new_status.order_sequence}'
                })
        
        # Save the updated instance
        updated_instance = serializer.save()
        
        # If status changed, create a new status history entry
        if new_status and new_status != old_status:
            ApplicationAssignedUserStatuses.objects.create(
                application_id=updated_instance,
                status_id=new_status,
                assigned_user_id=self.request.user,
                notes=status_notes or f"Status changed from {old_status} to {new_status}"
            )
        # If status_notes provided without status change, update the latest status history entry
        elif status_notes and updated_instance.current_status:
            latest_status = ApplicationAssignedUserStatuses.objects.filter(
                application_id=updated_instance,
                status_id=updated_instance.current_status
            ).order_by('-created_at').first()
            
            if latest_status:
                latest_status.notes = status_notes
                latest_status.save()
    
    def perform_destroy(self, instance):
        """
        Override to implement soft delete instead of hard delete.
        Uses the delete() method from SoftDeleteModel.
        """
        instance.delete()  # This calls the soft delete by default
