from django import forms
from django.contrib.auth.models import Group
from django.contrib.postgres.forms import SimpleArrayField, SplitArrayWidget

from .models import User, Profile, City, _


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': str(_("Username")) + "/" + str(_("Phone")) + "/" + str(_("Email"))
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': _("Password")
            }
        )
    )


class OtpForm(forms.Form):
    code = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _('Code')
            }
        )
    )


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("Username")
            }
        )
    )
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("First Name")
            }
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("Last Name")
            }
        )
    )
    phones = SimpleArrayField(forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("Phone Number")
            }
        ), help_text=_("if you have multiple phones, enter them separated by a coma.")
    ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': _("Password")
            }
        )
    )
    c_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': _("Confirm Password")
            }
        ), label=_('Confirm Password')
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                'placeholder': _("Email")
            }
        )
    )
    user_type = forms.ChoiceField(widget=forms.HiddenInput,
                                  choices=(('C', _('Client')), ('S', _('Staff')), ('A', _('Admin'))))

    class Meta:
        model = User
        fields = ['username', "first_name", "last_name", 'user_type', 'phones', 'email']

    def clean(self):
        super(RegistrationForm, self).clean()
        if not self.cleaned_data.get('password') == self.cleaned_data.get('c_password'):
            raise forms.ValidationError(_("Un-matching passwords!"))

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.save()

        user_type = self.cleaned_data['user_type']
        if user_type == 'C':
            group, created = Group.objects.get_or_create(name='Client')
            user.groups.add(group)

        user.save()
        return user


class ProfileForm(forms.ModelForm):
    user = forms.ModelChoiceField(User.objects.all(), empty_label=_('Choose a user'))
    photo = forms.ImageField(allow_empty_file=True)
    address = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _('Address')
            }
        )
    )
    city = forms.ModelChoiceField(City.objects.all(), empty_label=_('Select a city'), required=False)
    birth_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'placeholder': _('Birth Date')
            }
        )
    )

    class Meta:
        model = Profile
        fields = ['user', 'photo', 'address', 'city', 'birth_date', 'gender']


class CreateStaffForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("Username")
            }
        )
    )
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("First Name")
            }
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("Last Name")
            }
        )
    )
    phones = SimpleArrayField(forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _("Phone Number")
            }
        ), help_text=_("if you have multiple phones, enter them separated by a coma.")
    ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': _("Password")
            }
        )
    )
    c_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': _("Confirm Password")
            }
        )
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                'placeholder': _("Email")
            }
        )
    )
    user_type = forms.ChoiceField(widget=forms.HiddenInput,
                                  choices=(('C', _('Client')), ('S', _('Staff')), ('A', _('Admin'))))

    class Meta:
        model = User
        fields = ['username', "first_name", "last_name", 'user_type', 'phones', 'email']

    def clean(self):
        super(CreateStaffForm, self).clean()
        if not self.cleaned_data.get('password') == self.cleaned_data.get('c_password'):
            raise forms.ValidationError(_("Un-matching passwords!"))

    def save(self, commit=True):
        user = super(CreateStaffForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_staff = True
        user.save()

        user_type = self.cleaned_data['user_type']
        if user_type == 'S':
            group, created = Group.objects.get_or_create(name='Staff')
            user.groups.add(group)

        user.save()
        return user
