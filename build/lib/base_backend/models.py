from datetime import date

from . import SETTINGS
from django.db import models
from django.db.models import Func
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from .validators import phone_validator

from django.utils.translation import gettext_lazy as _

do_nothing = models.DO_NOTHING
cascade = models.CASCADE


class BaseModel(models.Model):
    """
    Base Model with creation and update timestamps.
    """
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DeletableModel(BaseModel):
    """
    Soft delete Base model
    """
    visible = models.BooleanField(default=True)

    def delete(self, using=None, keep_parents=False):
        self.visible = False
        self.save()

    class Meta:
        abstract = True


class SmsVerification(BaseModel):
    """
    Basic table for recording OTPs for sms verifications.
    """
    otp_code = models.CharField(max_length=5)
    number = models.CharField(validators=[phone_validator], max_length=255, editable=False)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return "{} is {}".format(self.number, 'Confirmed' if self.confirmed else 'Not Confirmed')

    class Meta:
        abstract = not SETTINGS.get("USE_BASE_BACKEND_OTP_TABLE", False)


class PasswordReset(BaseModel):
    """
    Basic table for recording password resets requests, works either with email or sms.
    the sms logic is:
    when a user requests a password reset from his phone, I generate a token and an otp code.
    the otp code is sent via sms, and the token is returned to the phone, once the user inputs the otp code in his phone
    it will be sent back along with the token for verification.
    """
    token = models.CharField(editable=False, max_length=255, null=False)
    used = models.BooleanField(default=False)
    email = models.EmailField(editable=False, null=True, blank=True)
    phone = models.CharField(max_length=20, editable=False, null=True, blank=True)
    otp_code = models.CharField(max_length=5, editable=False, null=True, blank=True)

    class Meta:
        abstract = not SETTINGS.get("USE_BASE_BACKEND_RESET_PASSWORD_TABLE", False)


# Basic regions models

class Region(BaseModel):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    name_ar = models.CharField(max_length=255, verbose_name=_('Arabic Name'))
    name_fr = models.CharField(max_length=255, verbose_name=_('English Name'))

    def __str__(self):
        return "{0}".format(self.name)

    class Meta:
        verbose_name = _('Region')
        verbose_name_plural = _("Regions")
        abstract = not SETTINGS.get("USE_BASE_BACKEND_REGIONS", False)


class State(BaseModel):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    name_ar = models.CharField(max_length=255, verbose_name=_('Arabic Name'))
    name_fr = models.CharField(max_length=255, verbose_name=_('English Name'))
    matricule = models.IntegerField(verbose_name=_('Matricule'))
    code_postal = models.IntegerField(verbose_name=_('Postal Code'))
    region = models.ForeignKey('Region', verbose_name=_('Region'), on_delete=do_nothing)

    def __str__(self):
        return "{0} {1}".format(self.matricule, self.name)

    class Meta:
        verbose_name = _('State')
        verbose_name_plural = _("States")
        abstract = not SETTINGS.get("USE_BASE_BACKEND_REGIONS", False)


class City(BaseModel):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    name_ar = models.CharField(max_length=255, verbose_name=_('Arabic Name'))
    name_en = models.CharField(max_length=255, verbose_name=_('English Name'))
    code_postal = models.IntegerField(verbose_name=_('Postal Code'))
    state = models.ForeignKey('State', on_delete=models.DO_NOTHING, related_name='cities', verbose_name=_('State'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _("Cities")
        abstract = not SETTINGS.get("USE_BASE_BACKEND_REGIONS", False)


# Basic Authentication Models


class User(AbstractUser):
    if SETTINGS.get("USER_TYPES", None):
        USER_TYPES = SETTINGS.get("USER_TYPES")
    else:
        USER_TYPES = (('C', _('Client')), ('S', _('Staff')), ('A', _('Admin')))

    if SETTINGS.get("PHONE_VALIDATOR", None):
        model_phone_validator = SETTINGS.get("PHONE_VALIDATOR")
    else:
        model_phone_validator = phone_validator

    notification_token = models.CharField(max_length=255, unique=True, blank=True, null=True)
    phones = ArrayField(base_field=models.CharField(
        _("Phone Number"),
        max_length=50,
        validators=[model_phone_validator],
        unique=True,
    ))
    is_active = models.BooleanField(
        _('Active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    user_type = models.CharField(
        _("Type"),
        max_length=1,
        choices=USER_TYPES,
        help_text=_("The user's type can be one of the available choices, "
                    "Client, Staff or Admin."),
    )

    visible = models.BooleanField(default=True)

    if SETTINGS.get("USERNAME_FIELD", None):
        USERNAME_FIELD = SETTINGS.get("USERNAME_FIELD")
    else:
        USERNAME_FIELD = "username"

    if SETTINGS.get("REQUIRED_FIELDS", None):
        REQUIRED_FIELDS = SETTINGS.get("REQUIRED_FIELDS")
    else:
        REQUIRED_FIELDS = [USERNAME_FIELD, "password"]

    @property
    def full_name(self):
        return super().get_full_name()

    @property
    def confirmed_phone(self) -> bool:
        """
        under development.
        """
        return True

    @property
    def confirmed_email(self) -> bool:
        """
        under development
        """
        return False

    def delete(self, using=None, keep_parents=False):
        """
        upon user delete we make it invisible so it won't selected and inactive so it can't be logged in with.
        """
        self.visible = False
        self.is_active = False
        self.save()

    def __str__(self):
        return self.full_name

    class Meta:
        abstract = not SETTINGS.get("USE_BASE_BACKEND_USER_MODEL", False)


class Profile(DeletableModel):
    if SETTINGS.get("GENDERS", None):
        GENDERS = SETTINGS.get("GENDERS")
    else:
        GENDERS = (('M', 'Male'), ('F', 'Female'))

    user = models.OneToOneField('User', on_delete=do_nothing, related_name='profile')
    photo = models.ImageField(
        _('Profile Picture'),
        upload_to='profile/',
        help_text=_("the user's profile picture."),
        blank=True,
        null=True
    )
    address = models.CharField(_("Address"), max_length=255, null=True)
    city = models.ForeignKey('City', on_delete=do_nothing, null=True, blank=True, related_name='profiles',
                             verbose_name=_('City'))
    birth_date = models.DateField(_('Birth Date'), blank=True, null=True)
    gender = models.CharField(choices=GENDERS, max_length=1, default='M', verbose_name=_('Gender'), null=True)

    @property
    def age(self) -> int:
        today = date.today()
        dob = self.birth_date
        before_dob = (today.month, today.day) < (dob.month, dob.day)
        return today.year - self.birth_date.year - before_dob

    @property
    def profile_picture(self):
        try:
            return self.photo.url
        except ValueError:
            return ""

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')
        abstract = not SETTINGS.get("USE_BASE_BACKEND_PROFILE_MODEL", False)


class Round(Func):
    """
    aggregation function rounds the decimal (float/double) to 2 decimal digits.
    """

    def __ror__(self, other):
        pass

    def __rand__(self, other):
        pass

    function = 'ROUND'
    arity = 2


class Month(Func):
    """
    aggregation function extracts the month number from the database date or timestamp field.
    """
    function = 'EXTRACT'
    template = '%(function)s(MONTH from %(expressions)s)'
    output_field = models.IntegerField()
