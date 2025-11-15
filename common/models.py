from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted objects by default."""
    
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class SoftDeleteModel(models.Model):
    """Abstract base model that provides soft delete functionality."""
    
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Access all objects including deleted
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False, hard=False):
        """
        Soft delete by default. Use hard=True for permanent deletion.
        """
        if hard:
            return super().delete(using=using, keep_parents=keep_parents)
        
        self.deleted_at = timezone.now()
        self.save(using=using)
    
    def is_deleted(self):
        """Check if object is soft-deleted."""
        return self.deleted_at is not None
