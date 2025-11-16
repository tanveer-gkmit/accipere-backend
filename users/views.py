from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import jwt

from .models import User
from .serializers import (
    UserSerializer, 
    UserCreateSerializer, 
    UserUpdateSerializer,
    SetPasswordSerializer
)
from common.permissions import IsAdmin, IsAdminOrSelf
from common.email_utils import send_set_password_email


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users (Administrator only).
    
    Endpoints:
    - GET    /api/users/                  - List all users
    - POST   /api/users/                  - Create user
    - GET    /api/users/{id}/             - Retrieve user
    - PUT    /api/users/{id}/             - Update user
    - PATCH  /api/users/{id}/             - Partial update user
    - DELETE /api/users/{id}/             - Soft delete user
    - POST   /api/users/set-password/     - Set password via setup link (public)
    """
    queryset = User.objects.filter(deleted_at__isnull=True)
    permission_classes = [IsAdmin]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'set_password':
            return SetPasswordSerializer
        return UserSerializer
    
    def get_permissions(self):
        """
        Set permissions based on action:
        - list: Admin only
        - retrieve: Admin or self
        - create: Admin only
        - update/partial_update: Admin or self (but only admin can change role)
        - destroy: Admin only
        - set_password: Public (no auth)
        """
        if self.action == 'set_password':
            return [AllowAny()]
        elif self.action == 'list':
            return [IsAdmin()]
        elif self.action == 'retrieve':
            return [IsAuthenticated(), IsAdminOrSelf()]
        elif self.action == 'create':
            return [IsAdmin()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsAdminOrSelf()]
        elif self.action == 'destroy':
            return [IsAdmin()]
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        """
        Create a new user and send password setup email.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate password setup token (expires in 2 days)
        setup_token = self._generate_setup_token(user)
        
        # Create setup link
        setup_link = f"{settings.FRONTEND_URL}/set-password?token={setup_token}"
        
        # Send email
        email_sent = send_set_password_email(
            receiver_email=user.email,
            user_name=user.get_full_name(),
            setup_link=setup_link
        )
        
        # Return response
        response_data = UserSerializer(user).data
        response_data['email_sent'] = email_sent
        
        return Response(
            response_data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """
        Update user. Only admins can change role.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Check if user is trying to change role
        if 'role' in request.data:
            # Only admins can change role
            if not (request.user.role and request.user.role.name == 'Administrator'):
                return Response(
                    {"error": "Only administrators can change user roles"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Partial update user. Only admins can change role.
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Soft delete a user by setting deleted_at timestamp.
        """
        user = self.get_object()
        user.deleted_at = timezone.now()
        user.is_active = False
        user.save()
        
        return Response(
            {"message": "User deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=False, methods=['post'], url_path='set-password')
    def set_password(self, request):
        """
        Public endpoint for users to set their password via setup link.
        Token contains user_id and expiration time.
        """
        token = request.data.get('token')
        
        if not token:
            return Response(
                {"error": "Token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Decode and validate token
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            user_id = payload.get('user_id')
            exp_time = payload.get('exp')
            
            # Check if token is expired
            if timezone.now().timestamp() > exp_time:
                return Response(
                    {"error": "Setup link has expired"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get user
            user = User.objects.get(id=user_id, deleted_at__isnull=True)
            
            # Check if user is already active and has password set
            if user.is_active and user.password:
                return Response(
                    {"error": "Password has already been set for this account"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        except jwt.ExpiredSignatureError:
            return Response(
                {"error": "Setup link has expired"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.InvalidTokenError:
            return Response(
                {"error": "Invalid setup link"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validate and set password
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user.set_password(serializer.validated_data['password'])
        user.is_active = True  # Activate user after password is set
        user.save()
        
        return Response(
            {"message": "Password set successfully. You can now login."},
            status=status.HTTP_200_OK
        )
    
    def _generate_setup_token(self, user):
        """
        Generate JWT token for password setup link.
        Token expires in 2 days and contains user_id.
        """
        expiration = timezone.now() + timedelta(days=2)
        
        payload = {
            'user_id': user.id,
            'email': user.email,
            'exp': int(expiration.timestamp()),
            'iat': int(timezone.now().timestamp()),
            'type': 'password_setup'
        }
        
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        
        return token
