"""
adapted from django's ModelBackend, just adding the possibility of authenticating with different fields (phone, email)
 in addition to the USERNAME field.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

UserModel = get_user_model()


class PhoneOrEmailBackend(ModelBackend):
    def authenticate(self, request, username: str = None, password: str = None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            user = UserModel.objects.get(Q(phone__iexact=username) | Q(email__iexact=username))
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
