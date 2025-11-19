from rest_framework import serializers
from django.utils import timezone
from .models import User
from roles.models import Role
from common.permissions import IsRecruiter
from applications.models import Applications


class SimpleUserSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for User model.
    Returns only id, email, name, and role name.
    Can be accessed by recruiters.
    """
    name = serializers.CharField(source='get_full_name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role_name']
        read_only_fields = ['id', 'email', 'name', 'role_name']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with role details.
    """
    role_name = serializers.CharField(source='role.name', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    is_password_set = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'role_name', 'is_active', 'is_staff', 'is_password_set',
            'created_at', 'updated_at', 'last_login', 'deleted_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login', 'deleted_at']
    
    def get_is_password_set(self, obj):
        """Check if user has a usable password set."""
        return obj.has_usable_password()


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
        # Explicitly set unusable password - will be set via the setup link
        user.set_unusable_password()
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing users.
    Email, role, and is_active can only be changed by administrators.
    """
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), required=False)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'is_active']
    
    def validate_email(self, value):
        """
        Ensure email is unique (excluding current user).
        Only administrators can change email.
        """
        request = self.context.get('request')
        user = self.instance
        
        # If email is being changed
        if user and user.email != value:
            # Check if user is admin
            if not (request and request.user.role and request.user.role.name == 'Administrator'):
                raise serializers.ValidationError("Only administrators can change user email.")
        
        # Check uniqueness
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
    
    def validate_is_active(self, value):
        """Only administrators can change is_active status."""
        request = self.context.get('request')
        if request and self.instance:
            # If is_active is being changed
            if self.instance.is_active != value:
                # Check if user is admin
                if not (request.user.role and request.user.role.name == 'Administrator'):
                    raise serializers.ValidationError("Only administrators can change user active status.")
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



class UserApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for applications assigned to a user.
    Shows application details with job and status information.
    """
    job_title = serializers.CharField(source='job_id.title', read_only=True)
    current_status_name = serializers.CharField(source='current_status.name', read_only=True)
    applicant_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Applications
        fields = [
            'id', 'applicant_name', 'email', 'phone_no',
            'job_id', 'job_title', 'current_status', 'current_status_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_applicant_name(self, obj):
        """Return full name of the applicant."""
        return f"{obj.first_name} {obj.last_name}"
