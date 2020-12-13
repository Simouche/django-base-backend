from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model


def super_user_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='admin:login'):
    """
    view's permission decorator, to allow only the super user to see the view. created it since django only has the
    staff_only decorator.
    """
    actual_decorator = user_passes_test(lambda u: u.is_active and u.is_superuser,
                                        login_url=login_url,
                                        redirect_field_name=redirect_field_name)
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


def api_login_required_factory():
    """

    """

    def decorator(function):
        @wraps(function)
        def wrapped_function(*args, **kwargs):
            request = args[0]
            if request and request.headers.get('authorization') is not None:
                user = get_user_model().objects.filter(access_token=request.headers.get('authorization'))
                if user.exists():
                    return function(*args, **kwargs)
            raise PermissionDenied

        return wrapped_function

    return decorator
