from django.apps import AppConfig
from django.db.models.signals import post_migrate

class ApplicationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'applications'
    
    def ready(self):
        def create_default_statuses(sender, **kwargs):
            from .models import ApplicationStatuses

            default_statuses = [
                "HR Screening",
                "Technical Screening",
                "Interview 1",
                "Interview 2",
                "HR Interview",
                "Offer Sent",
                "Joined",
                "Rejected"
            ]

            for index, status_name in enumerate(default_statuses):
                ApplicationStatuses.objects.get_or_create(
                    name=status_name,
                    defaults={
                        "description": status_name,
                        "order_sequence": index
                    }
                )

        post_migrate.connect(create_default_statuses, sender=self)
