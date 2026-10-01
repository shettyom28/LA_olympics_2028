from rest_framework.permissions import BasePermission


class IsServiceAccount(BasePermission):
    """Allow access only to internal service accounts (users in the 'system-service-accounts' group)."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.groups.filter(name='system-service-accounts').exists()
        )

class IsStaffUser(BasePermission):
    """Allow access only to users in the 'Staff' group or superusers."""
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and (request.user.is_staff or request.user.groups.filter(name='Staff').exists())
        )
