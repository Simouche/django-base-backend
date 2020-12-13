import os
import random
import secrets
from functools import wraps

from json import JSONDecodeError

import requests
from . import SETTINGS
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db import models
from django.db.models import Q, Func
from django.shortcuts import get_object_or_404

from . import get_password_reset_table, get_otp_verification_table, get_send_sms_function


# from restaurant.settings import EMAIL_HOST_USER


def generate_token(length=32):
    """
    generates a token with the specified length (default 32), this is being used as access token
    :return:
    """
    return secrets.token_hex(length)


def generate_alphabetic_random_code() -> str:
    """
    generates a 5 alphabetic capital characters random code, this is being used as OTP.
    :return: String
    """
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                'V', 'W', 'X', 'Y', 'Z']
    random_alphabet = random.choice(alphabet)
    randoms = [random_alphabet]
    for i in range(4):
        randoms.append(str(random.randint(0, 9)))

    code = ''.join(randoms)

    return code


def generate_all_chars_random_code() -> str:
    """
    generates a 5 characters random code, this is being used as OTP.
    :return: String
    """
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                'V', 'W', 'X', 'Y', 'Z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '_', '-', '%', '$', '^', '?',
                '!', '.', ',', ';']
    random_alphabet = random.choice(alphabet)
    randoms = [random_alphabet]
    for i in range(4):
        randoms.append(str(random.randint(0, 9)))

    code = ''.join(randoms)

    return code


def generate_random_password() -> str:
    """
    generates a random password of 15 chars length from literally all most used chars.
    """
    password = ''
    for i in range(3):
        password += generate_all_chars_random_code()

    return password


def phone_sms_verification(phone: str):
    """
    creates a tuple of a random code (OTP) and a phone number and stores them in the otp verification table,
    to verify the phone number provided by a user.
    requires the use of the sms verification table, either implementing your own or using the one provided by the *
    library.
    :param phone: phone number provided by the user
    :return:
    """
    code = generate_alphabetic_random_code()
    sms = get_otp_verification_table().objects.filter(otp_code=code, confirmed=False)

    while sms.exists():
        code = generate_alphabetic_random_code()
        sms = get_otp_verification_table().objects.filter(otp_code=code, confirmed=False)

    get_otp_verification_table().objects.create(otp_code=code, number=phone)
    message = "use this code: {0}, to confirm your {1} account phone number.".format(code, SETTINGS.get("APP_NAME"))
    send_sms(phone, message)


def phone_reconfirmation(phone: get_otp_verification_table()):
    message = "use this code: {0}, to confirm your {1} account phone number.".format(phone.otp_code,
                                                                                     SETTINGS.get("APP_NAME"))
    send_sms(phone.number, message)


def send_sms(phone, message):
    """
    send an sms containing the message parameter to the phone parameter
    :param phone: the target phone
    :param message: the message to be sent
    :return:
    """
    send_sms_function = get_send_sms_function()
    send_sms_function(phone=phone, message=message)


def reset_user_password(token, attr, password):
    """
    resets the user password, after checking the reset credentials(phone,token) from the PasswordReset table
    and verifying that the PasswordReset instance has not been used (verified over OTP).
    :param token: the ResetPassword instance token credential
    :param attr: the users phone number provided also in the PasswordReset
    :param password: the new password
    :return: True if the password
    """
    password_reset = get_object_or_404(get_password_reset_table(), Q(Q(phone=attr) | Q(email=attr)), token=token)
    if not password_reset.used:
        password_reset.used = True
        password_reset.save()
        user = get_object_or_404(get_user_model(), Q(Q(phone=attr) | Q(email=attr)))
        user.set_password(password)
        user.save()
        return True
    else:
        return False


# def verify_sms_code_for_password_reset(code, token):
#     """
#     verifies OTP code from PasswordReset table, and set it as used if it exists
#     :param code: OTP
#     :param token: token provided to the user
#     :return: raises Http404 if the credentials don't exist or already used, else returns true
#     """
#     get_object_or_404(get_password_reset_table(), code=code, token=token, used=False)
#     return True


def verify_sms_code_for_phone_confirmation(code: str):
    """
    verifies if the code provided belongs to an sms verification operation
    :param code:
    :return:
    """
    verification = get_otp_verification_table().objects.filter(otp_code=code)
    if verification.exists():
        verification = verification.first()
        verification.confirmed = True
        verification.save()
        return True, verification.number
    return False, False


def activate_user_over_otp(code):
    """
    verifies the provided code if it belongs to account confirmation OTP then activates the user
    :param code:
    :return:
    """
    status, response = verify_sms_code_for_phone_confirmation(code)
    if status:
        user = get_user_model().objects.filter(phone=response)
        the_user = user.first()
        the_user.is_active = True
        the_user.save()
        return True
    return False


def set_notification_token(user, token):
    user.notifications_token = token
    user.save()
    return {'status': True,
            'message': 'Success'}


def api_errors_extractor(form_errors) -> list:
    """
    extracts the errors from a form's error property to a more readable and serializable format.
    return: list
    """
    if form_errors:
        list_keys = list(form_errors.keys())
        list_values = list(form_errors.values())
        values = []
        for value in list_values:
            for value1 in value:
                values.append(value1)
        return list(zip(list_keys, values))


def handle_uploaded_file(file, directory) -> None:
    """
    Stores the file at the desired location.
    It is memory friendly, it can be used with large files.
    """
    with open(directory, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def send_email(subject: str, email: str, message: str) -> int:
    """
    still under development.
    """
    return send_mail(
        subject=subject,
        message=message,
        # from_email=EMAIL_HOST_USER,
        recipient_list=email if isinstance(email, list) else [email]
    )


def get_current_week():
    """
    return: the current week number value from (1-52)
    """
    from datetime import date
    return date.today().isocalendar()[1]


def get_current_year():
    """
    return: the current year.
    """
    from datetime import date
    return date.today().isocalendar()[0]


def get_current_day():
    """
    return the current day number value from (1-7).
    """
    from datetime import date
    return date.today().isocalendar()[2]


def is_ajax(request) -> bool:
    """
    since django 3.0 the function is_ajax has been deprecated from the HTTPRequest objects, so i extracted it as a
    separate function.
    request: HTTPRequest object.
    return: bool.
    """
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def is_app_ready() -> bool:
    """
    in some situations I had to start executing/doing some work as soon as the server starts. But due to django's
    special way of starting the server and if my work requires the use of models or anything related to the
    django's startup procedure i received app not ready error.
    wrapping the execution of my work with this function helped me working around that.
    return: bool.
    """
    return os.environ.get('RUN_MAIN', None) != 'true'
