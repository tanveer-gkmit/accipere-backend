from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from common.models import SoftDeleteModel
import uuid

User = get_user_model()


class Jobs(SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Employment type choices
    EMPLOYMENT_TYPES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Internship', 'Internship'),
    ]
    
    # Experience level choices
    EXPERIENCE_LEVELS = [
        ('Entry', 'Entry'),
        ('Mid', 'Mid'),
        ('Senior', 'Senior'),
        ('Lead', 'Lead'),
    ]
    
    # Status choices
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Closed', 'Closed'),
    ]

    # Basic fields
    title = models.CharField(max_length=255)
    description = models.TextField()
    employment_type = models.CharField(max_length=20,choices=EMPLOYMENT_TYPES)
    location = models.CharField(max_length=255)
    department = models.CharField()
    experience_level = models.CharField(max_length=20,choices=EXPERIENCE_LEVELS)

    salary_min = models.PositiveIntegerField(null=True,blank=True)
    salary_max = models.PositiveIntegerField(null=True,blank=True)

    requirements = models.TextField()
    benefits = models.TextField(blank=True)
    posted_by_user_id = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)

    closing_date = models.DateTimeField(null=True,blank=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def clean(self):
        super().clean()

        if self.status == "Closed" and not self.closing_date :
            self.closing_date = timezone.now()
        elif self.closing_date : 
            self.closing_date = None
        
    def __str__(self):
        return self.title