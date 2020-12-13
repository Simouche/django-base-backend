from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

SETTINGS = None


def load_settings():
    global SETTINGS
    try:
        SETTINGS = settings.BASE_BACKEND
    except AttributeError:
        SETTINGS = {}


load_settings()


def get_password_reset_table():
    """
    Return the Password Reset model that is active in this project.
    """
    if SETTINGS.get("USE_BASE_BACKEND_RESET_PASSWORD_TABLE", False):
        return django_apps.get_model("base_backend.PasswordReset", require_ready=False)
    else:
        try:
            return django_apps.get_model(SETTINGS.get("PASSWORD_RESET_TABLE", None), require_ready=False)
        except ValueError:
            raise ImproperlyConfigured("PHONE_VERIFICATION_OTP_TABLE must be of the form 'app_label.model_name'")
        except LookupError:
            raise ImproperlyConfigured(
                "PHONE_VERIFICATION_OTP_TABLE refers to model '%s' that has not been installed"
                % settings.PASSWORD_RESET_TABLE)


def get_otp_verification_table():
    """
    Return the OTP Verification model that is active in this project.
    """
    if SETTINGS.get("USE_BASE_BACKEND_OTP_TABLE", False):
        return django_apps.get_model("base_backend.SmsVerification", require_ready=False)
    else:
        try:
            return django_apps.get_model(SETTINGS.get("PHONE_VERIFICATION_OTP_TABLE", None), require_ready=False)
        except ValueError:
            raise ImproperlyConfigured("PHONE_VERIFICATION_OTP_TABLE must be of the form 'app_label.model_name'")
        except LookupError:
            raise ImproperlyConfigured(
                "PHONE_VERIFICATION_OTP_TABLE refers to model '%s' that has not been installed"
                % settings.PHONE_VERIFICATION_OTP_TABLE)


def get_send_sms_function():
    """
    return the implemented function for sending sms, it should accept the named params:
    phone: Phone number.
    message: A message.
    """

    if SETTINGS.get("SEND_SMS_FUNC", None):
        return settings.SEND_SMS_FUNC
    else:
        raise ImproperlyConfigured("you are trying to send an sms, but the SEND_SMS_FUNC is not provided in the"
                                   " settings.")
