from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from common.permissions import IsRecruiter, IsAdmin 
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import ApplicationStatuses
from .serializers import ApplicationStatusesSerializer

class ApplicationStatusesViewSet(viewsets.ModelViewSet):
    queryset = ApplicationStatuses.objects.all()
    serializer_class = ApplicationStatusesSerializer

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
                {"id": 1, "order_sequence": 0},
                {"id": 3, "order_sequence": 1},
                {"id": 2, "order_sequence": 2}
            ]
        }
        """
        items = request.data.get('items', [])
        
        if not items:
            return Response(
                {'error': 'No items provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            with transaction.atomic():
                for item in items:
                    ApplicationStatuses.objects.filter(
                        id=item['id']
                    ).update(order_sequence=item['order_sequence'])
        except Exception as e:
            return Response(
                {'error': f"Internal Server Error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response({'message': 'Order updated successfully'})
