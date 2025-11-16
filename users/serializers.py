from rest_framework import serializers
from django.utils import timezone
from .models import User
from roles.models import Role


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with role details.
    """
    role_name = serializers.CharField(source='role.name', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'role_name', 'is_active', 'is_staff',
            'created_at', 'updated_at', 'last_login', 'deleted_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login', 'deleted_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users (Administrator only).
    Password is not set here - user receives email with setup link.
    """
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role']
    
    def validate_email(self, value):
        """Ensure email is unique (including soft-deleted users)."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def create(self, validated_data):
        """Create user without password - will be set via email link."""
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data['role'],
            is_active=False  # Inactive until password is set
        )
        # Don't set password here - it will be set via the setup link
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing users.
    Role can only be changed by administrators.
    """
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), required=False)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'is_active']
    
    def validate_email(self, value):
        """Ensure email is unique (excluding current user)."""
        user = self.instance
        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_role(self, value):
        """
        Validate role change.
        This is a backup validation - main check is in the view.
        """
        request = self.context.get('request')
        if request and self.instance:
            # If role is being changed
            if self.instance.role != value:
                # Check if user is admin
                if not (request.user.role and request.user.role.name == 'Administrator'):
                    raise serializers.ValidationError("Only administrators can change user roles.")
        return value


class SetPasswordSerializer(serializers.Serializer):
    """
    Serializer for setting password via setup link.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Ensure passwords match."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return data
