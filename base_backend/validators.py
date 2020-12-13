from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

"""
Algerian phone numbers validator.
"""
phone_validator = RegexValidator('^\\+?[0-9]{,12}$', _('The phone number you entered is not valid '
                                                       'it must be of the international format.'
                                                       'example \'+213799136332\''),
                                 'Invalid PhoneNumber')
"""
username validator for alphanumeric usernames starting with a letter and contains only an underscore as a special
 character
"""
username_validator = RegexValidator('^[a-zA-Z]{1}[a-zA-Z_0-9]{6,}$', _('The username you entered is not valid '
                                                                       'the allowed characters are:\n '
                                                                       'a-z, A-Z, 0-9, \'_\''), 'Invalid Username')

"""
8 chars length password validator.
"""
password_validator = RegexValidator('.{8,}', _('Invalid password. Password must at least contain 8'
                                               ' characters.'), 'Invalid Password')

"""
Names validator, allows only letters and spaces, cannot be blank.
"""
names_validator: RegexValidator = RegexValidator('^[a-zA-Z]+( [a-zA-Z]+)*$', _('Invalid name, names must contain only '
                                                                               'Alphabetic characters, '
                                                                               'without leading or '
                                                                               'trailing spaces.'), 'Invalid Name')

"""
address validator, still under development.
"""
address_validator = RegexValidator('^[0-9]{,5}[,. ]{,1}[ a-zA-Z]{5,}([0-9]{,5}[ a-zA-Z]{5,})?$',
                                   _('Invalid address, i\'m sorry i can\'t explain the pattern here.'),
                                   'Invalid Address')
"""
Algerian Registre Commerce number validator.
"""
register_validator = RegexValidator('^[0-9]{2}[a-zA-Z][0-9]{7}$', _('Invalid commerce register number or wrong format,'
                                                                    ' the format should be'
                                                                    ' "XXYXXXXXXX" (X=number, Y=Alphabet) '))
"""
Algerian Numero D'identifiant Fiscal validator.
"""
nif_validator = RegexValidator('^[0-9]{15}$', _('Invalid NIF number ,'
                                                ' the format should be'
                                                ' "XXXXXXXXXXXXXXX" (X=number) '))
