from django.db import models


from common.models import SoftDeleteModel
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator, MaxValueValidator
User = get_user_model()
from jobs.models import Jobs
from django.db.models import UniqueConstraint, Deferrable


class ApplicationStatuses(models.Model):
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField()
    order_sequence = models.IntegerField(editable=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order_sequence']
        constraints = [
            UniqueConstraint(
                fields=['order_sequence'],
                name='unique_order_sequence',
                deferrable=Deferrable.DEFERRED,  # Checked at transaction end
            )
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Only auto-assign order_sequence for new instances
        if self.pk is None:
            max_order = ApplicationStatuses.objects.aggregate(
                models.Max('order_sequence')
            )['order_sequence__max']
            self.order_sequence = (max_order or 0) + 1
        super().save(*args, **kwargs)



class Applications(SoftDeleteModel):

    INDIAN_PHONE_REGEX = RegexValidator(
    regex=r'^(?:\+91)?[6-9]\d{9}$',
    message="Enter a valid Indian phone number (e.g. 9876543210 or +919876543210)."
    )
    job_id = models.ForeignKey(Jobs,on_delete=models.CASCADE,related_name='applications')

    email = models.EmailField(db_index=True)
    phone_no = models.CharField(max_length=13,validators=[INDIAN_PHONE_REGEX])
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    resume = models.BinaryField()

    total_experience = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    relevant_experience = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    current_ctc = models.IntegerField(null=True,blank=True,validators=[MinValueValidator(0)])
    expected_ctc = models.IntegerField(null=True,blank=True,validators=[MinValueValidator(0)])

    notice_period = models.CharField(max_length=255,null=True,blank=True)

    current_job_title = models.CharField(max_length=255,null=True,blank=True)

    linkedin = models.URLField(max_length=255,null=True,blank=True)
    github = models.URLField(max_length=255,null=True,blank=True)

    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    zip_code = models.CharField(
        max_length=6,
        validators=[RegexValidator(r'^\d{6}$', 'Enter valid 6-digit PIN code')]
    )

    current_status = models.ForeignKey(
        ApplicationStatuses,
        on_delete=models.PROTECT,
        null=True,
        related_name='current_applications'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"





class ApplicationAssignedUserStatuses(SoftDeleteModel):

    application_id = models.ForeignKey(Applications,on_delete=models.CASCADE,related_name='status_history')
    status_id = models.ForeignKey(ApplicationStatuses,on_delete=models.RESTRICT,related_name='assignments')
    assigned_user_id = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=False,related_name="assigned_application_statuses")
    
    notes = models.TextField(blank=True,null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
