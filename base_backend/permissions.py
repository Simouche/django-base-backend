from django.core.exceptions import ImproperlyConfigured
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsReadOnly(BasePermission):
    """
    The request is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS)


class IsOwnerOrReadOnly(BasePermission):
    """
        Object-level permission to only allow owners of an object to edit it.
        Assumes the model instance has an `owner` attribute.
        """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        try:
            return getattr(obj, obj.OWNER_FIELD) == request.user
        except AttributeError:
            raise ImproperlyConfigured("If you want to use this permission, you should specify an OWNER_FIELD property"
                                       "in your object or extend the Owned Model from base_backend models")


class IsAdminOrIsOwner(BasePermission):
    """
    Allow only the user or an admin user to edit.
    """

    def has_object_permission(self, request, view, obj):
        try:
            return request.user.is_staff or getattr(obj, obj.OWNER_FIELD) == request.user
        except AttributeError:
            raise ImproperlyConfigured("If you want to use this permission, you should specify an OWNER_FIELD property"
                                       "in your object or extend the Owned Model from base_backend models")


class IsAdminOrReadOnly(BasePermission):
    """
    pretty self explanatory.
    """

    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS or request.user and request.user.is_staff)
