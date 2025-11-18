from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
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
from common.email_utils import send_set_password_email, send_reset_password_email


TOKEN_EXPIRY_DAYS = 2
PASSWORD_SETUP = 'password_setup'
PASSWORD_RESET = 'password_reset'


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users (Administrator only).
    
    Endpoints:
    - GET    /api/users/                      - List all users
    - POST   /api/users/                      - Create user
    - GET    /api/users/{id}/                 - Retrieve user
    - PUT    /api/users/{id}/                 - Update user
    - PATCH  /api/users/{id}/                 - Partial update user
    - DELETE /api/users/{id}/                 - Soft delete user
    - POST   /api/users/{id}/reset-password/  - Reset user password (admin only)
    - POST   /api/users/set-password/         - Set password via setup/reset link (public)
    """
    queryset = User.objects.filter(deleted_at__isnull=True)
    permission_classes = [IsAdmin]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        serializer_map = {
            'create': UserCreateSerializer,
            'update': UserUpdateSerializer,
            'partial_update': UserUpdateSerializer,
            'set_password': SetPasswordSerializer,
        }
        return serializer_map.get(self.action, UserSerializer)
    
    def get_permissions(self):
        """Set permissions based on action."""
        permission_map = {
            'set_password': [AllowAny()],
            'list': [IsAdmin()],
            'retrieve': [IsAuthenticated(), IsAdminOrSelf()],
            'create': [IsAdmin()],
            'update': [IsAuthenticated(), IsAdminOrSelf()],
            'partial_update': [IsAuthenticated(), IsAdminOrSelf()],
            'destroy': [IsAdmin()],
        }
        return permission_map.get(self.action, super().get_permissions())
    
    def create(self, request, *args, **kwargs):
        """Create a new user and send password setup email."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Send setup email
        email_sent = self._send_password_email(user, PASSWORD_SETUP)
        
        # Return response
        response_data = UserSerializer(user).data
        response_data['email_sent'] = email_sent
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update user. Role validation handled by serializer."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        """Partial update user."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete a user by setting deleted_at timestamp."""
        user = self.get_object()
        user.deleted_at = timezone.now()
        user.is_active = False
        user.save()
        
        return Response(
            {"message": "User deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=True, methods=['post'], url_path='reset-password')
    def reset_password(self, request, pk=None):
        """Admin-only endpoint to reset a user's password."""
        user = self.get_object()
        
        # Set password to unusable
        user.set_unusable_password()
        user.save()
        
        # Send reset email
        email_sent = self._send_password_email(user, PASSWORD_RESET)
        
        return Response(
            {
                "message": "Password reset successfully. Reset email sent to user.",
                "email_sent": email_sent
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'], url_path='set-password')
    def set_password(self, request):
        """Public endpoint for users to set password via setup/reset link."""
        token = request.data.get('token')
        if not token:
            return Response(
                {"error": "Token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate token and get user
        user, token_type = self._validate_token(token)
        
        # For new account setup, check if password already set
        if token_type == PASSWORD_SETUP and user.has_usable_password():
            return Response(
                {"error": "Password has already been set for this account"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate and set password
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user.set_password(serializer.validated_data['password'])
        user.is_active = True
        user.save()
        
        message = (
            "Password set successfully. You can now login."
            if token_type == PASSWORD_SETUP
            else "Password reset successfully. You can now login."
        )
        
        return Response({"message": message}, status=status.HTTP_200_OK)
    
    def _generate_token(self, user, token_type=PASSWORD_SETUP):
        """Generate JWT token for password setup/reset link."""
        expiration = timezone.now() + timedelta(days=TOKEN_EXPIRY_DAYS)
        now = timezone.now()
        
        payload = {
            'user_id': str(user.id),
            'email': user.email,
            'exp': int(expiration.timestamp()),
            'iat': int(now.timestamp()),
            'type': token_type
        }
        
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    def _validate_token(self, token):
        """Validate JWT token and return user and token type."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            
            user_id = payload.get('user_id')
            token_type = payload.get('type', PASSWORD_SETUP)
            exp_time = payload.get('exp')
            
            # Check expiration
            if timezone.now().timestamp() > exp_time:
                raise ValidationError({"error": "Link has expired"})
            
            # Get user
            user = User.objects.get(id=user_id, deleted_at__isnull=True)
            return user, token_type
            
        except jwt.ExpiredSignatureError:
            raise ValidationError({"error": "Link has expired"})
        except jwt.InvalidTokenError:
            raise ValidationError({"error": "Invalid link"})
        except User.DoesNotExist:
            raise ValidationError({"error": "User not found"})
    
    def _send_password_email(self, user, email_type):
        """Send password setup or reset email."""
        token = self._generate_token(user, email_type)
        link = f"{settings.FRONTEND_URL}/set-password?token={token}"
        
        if email_type == PASSWORD_SETUP:
            return send_set_password_email(
                receiver_email=user.email,
                user_name=user.get_full_name(),
                setup_link=link
            )
        else:
            return send_reset_password_email(
                receiver_email=user.email,
                user_name=user.get_full_name(),
                reset_link=link
            )
