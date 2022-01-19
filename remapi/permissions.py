from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS


class IsAPIUser(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return user.has_perm('remapi.is_api_user')