from django.apps import AppConfig


class RolesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'roles'
    
    def ready(self):
        from django.db.models.signals import post_migrate

        def create_default_roles(sender, **kwargs):
            from roles.models import Role
            default_roles = ['Administrator', 'Recruiter', 'Technical Evaluator']
            for role_name in default_roles:
                Role.objects.get_or_create(name=role_name)

        post_migrate.connect(create_default_roles, sender=self)
