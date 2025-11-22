from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import uuid

from roles.models import Role

class UserManager(BaseUserManager):
    """
    Custom user manager for User model with email as the unique identifier.
    """
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        """
        Create and save a regular user with the given email, first_name, last_name, and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        if not first_name:
            raise ValueError('The First Name field must be set')
        if not last_name:
            raise ValueError('The Last Name field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        
        # Validate password strength before setting it
        if password:
            try:
                validate_password(password, user=user)
            except ValidationError as e:
                raise ValueError(f"Password validation failed: {', '.join(e.messages)}")
            user.set_password(password)  # This uses Django's PBKDF2 password hashing
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        """
        Create and save a superuser with the given email, first_name, last_name, and password.
        Superusers are automatically assigned the Administrator role.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        # Superusers must have Administrator role
        if 'role' not in extra_fields:
            admin_role = Role.objects.get(name='Administrator')
            extra_fields['role'] = admin_role
        elif extra_fields['role'].name != 'Administrator':
            raise ValueError('Superuser must have Administrator role.')

        return self.create_user(email, first_name, last_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with email as the unique identifier.
    Extends AbstractBaseUser for authentication functionality.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    role = models.ForeignKey(
        Role,
        on_delete=models.RESTRICT,
        related_name='users',
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        """
        Return the user's full name.
        """
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        """
        Return the user's short name.
        """
        return self.first_name
