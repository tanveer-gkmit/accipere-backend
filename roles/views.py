from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Role
from .serializers import RoleSerializer


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving roles.
    Provides list and retrieve actions only (GET endpoints).
    
    Permissions:
    - list, retrieve: IsAuthenticated
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
