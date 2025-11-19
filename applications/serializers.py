from rest_framework import serializers
from .models import ApplicationStatuses, Applications, ApplicationAssignedUserStatuses
import magic


def validate_pdf_file(file):
    """Validate that uploaded file is a PDF using python-magic and within size limit"""
    # Check file size (max 5MB)
    if file.size > 5 * 1024 * 1024:
        raise serializers.ValidationError("Resume file size cannot exceed 5MB.")
    
    # Read the first 2048 bytes to detect file type
    file.seek(0)
    file_header = file.read(2048)
    file.seek(0)  # Reset file pointer
    
    # Detect MIME type using python-magic
    mime = magic.from_buffer(file_header, mime=True)
    
    if mime != 'application/pdf':
        raise serializers.ValidationError(
            f"Only PDF files are allowed. Detected file type: {mime}"
        )
    
    return file


class ApplicationStatusSerializer(serializers.ModelSerializer):
    """Full serializer for ApplicationStatuses with all fields"""
    class Meta:
        model = ApplicationStatuses
        fields = ['id', 'name', 'description', 'order_sequence', 'created_at', 'updated_at']
        read_only_fields = ['order_sequence', 'created_at', 'updated_at']


class ApplicationStatusSimpleSerializer(serializers.ModelSerializer):
    """Lightweight serializer for ApplicationStatuses (nested use)"""
    class Meta:
        model = ApplicationStatuses
        fields = ['id', 'name', 'description']


class ApplicationAssignedUserStatusSerializer(serializers.ModelSerializer):
    """Serializer for status history"""
    status_name = serializers.CharField(source='status_id.name', read_only=True)
    assigned_user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ApplicationAssignedUserStatuses
        fields = ['id', 'status_id', 'status_name', 'assigned_user_id', 
                  'assigned_user_name', 'notes', 'created_at']
        read_only_fields = ['created_at']
    
    def get_assigned_user_name(self, obj):
        if obj.assigned_user_id:
            return obj.assigned_user_id.get_full_name() or obj.assigned_user_id.username
        return None


class ApplicationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing applications"""
    job_title = serializers.CharField(source='job_id.title', read_only=True)
    current_status_name = serializers.CharField(source='current_status.name', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Applications
        fields = ['id', 'full_name', 'email', 'phone_no', 'job_id', 'job_title',
                  'current_status', 'current_status_name', 'created_at']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class ApplicationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for retrieving single application"""
    job_details = serializers.SerializerMethodField()
    current_status_details = ApplicationStatusSimpleSerializer(source='current_status', read_only=True)
    status_history = ApplicationAssignedUserStatusSerializer(many=True, read_only=True)
    resume_filename = serializers.SerializerMethodField()
    
    class Meta:
        model = Applications
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'deleted_at']
    
    def get_job_details(self, obj):
        return {
            'id': obj.job_id.id,
            'title': obj.job_id.title,
        }
    
    def get_resume_filename(self, obj):
        return f"{obj.first_name}_{obj.last_name}_resume.pdf" if obj.resume else None


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating applications"""
    resume_file = serializers.FileField(write_only=True, validators=[validate_pdf_file])
    status_notes = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = Applications
        fields = [
            'job_id', 'email', 'phone_no', 'first_name', 'last_name',
            'resume_file', 'total_experience', 'relevant_experience',
            'current_ctc', 'expected_ctc', 'notice_period', 'current_job_title',
            'linkedin', 'github', 'street', 'city', 'zip_code', 'status_notes'
        ]
    
    def create(self, validated_data):
        """Handle file upload and convert to binary"""
        resume_file = validated_data.pop('resume_file')
        validated_data.pop('status_notes', None)  # Remove status_notes, handled in perform_create
        
        # Read file content and store as binary
        validated_data['resume'] = resume_file.read()
        
        return super().create(validated_data)


class ApplicationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating applications"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    resume_file = serializers.FileField(write_only=True, required=False, validators=[validate_pdf_file])
    status_notes = serializers.CharField(write_only=True, required=False, allow_blank=True)
    assigned_user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(deleted_at__isnull=True, is_active=True),
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Applications
        fields = [
            'email', 'phone_no', 'first_name', 'last_name',
            'resume_file', 'total_experience', 'relevant_experience',
            'current_ctc', 'expected_ctc', 'notice_period', 'current_job_title',
            'linkedin', 'github', 'street', 'city', 'zip_code', 
            'current_status', 'status_notes', 'assigned_user_id'
        ]
    
    def update(self, instance, validated_data):
        """Handle optional file update"""
        resume_file = validated_data.pop('resume_file', None)
        # Don't pop status_notes and assigned_user_id - they're handled in perform_update
        validated_data.pop('status_notes', None)
        # Keep assigned_user_id in validated_data for perform_update to use
        
        if resume_file:
            validated_data['resume'] = resume_file.read()
        
        return super().update(instance, validated_data)
