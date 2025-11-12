from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Permission class that allows access only to users with Administrator role.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role and
            request.user.role.name == 'Administrator'
        )


class IsRecruiter(BasePermission):
    """
    Permission class that allows access to users with Administrator or Recruiter roles.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role and
            request.user.role.name in ['Administrator', 'Recruiter']
        )


class IsTechnicalEvaluator(BasePermission):
    """
    Permission class that allows access to users with Administrator, Recruiter, or Technical Evaluator roles.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role and
            request.user.role.name in ['Administrator', 'Recruiter', 'Technical Evaluator']
        )


class IsAdminOrSelf(BasePermission):
    """
    Permission class for object-level permissions.
    Allows access to administrators or the user themselves.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.user and
            request.user.is_authenticated and
            (
                (request.user.role and request.user.role.name == 'Administrator') or
                request.user == obj
            )
        )
