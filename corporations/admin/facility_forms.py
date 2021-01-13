from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from corporations.models import Facility, Branch

User = get_user_model()


class BranchInlineForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = 'name', 'is_main',

    def clean_is_main(self):
        main_flag_form = self.cleaned_data.get('is_main')
        if 'is_main' in self.changed_data and main_flag_form:
            have_main = Branch.objects.filter(facility=self.instance.facility, is_main=True).exists()
            if have_main:
                raise forms.ValidationError(f'Facility {self.instance.facility} already have a main branch.')
        return main_flag_form


class AddFacilityModelForm(forms.ModelForm):
    branch_name = forms.CharField(
        required=False,
        max_length=50,
        help_text='Branch name with default value = Default Branch'
    )
    username = forms.CharField(
        max_length=50,
        validators=[User.username_validator],
        help_text=_('Required. 50 characters or fewer. only contain lowercase letters or underscores.')
    )
    first_name = forms.CharField(required=False, max_length=30)
    last_name = forms.CharField(required=False, max_length=150)
    email = forms.EmailField(
        required=True,
        help_text=_('Required. valid email must be provided to use when contact with user.')
    )

    class Meta:
        model = Facility
        fields = 'uid', 'name', 'segment', 'branch_name', 'first_name', 'last_name', 'username', 'email',

    def clean_branch_name(self):
        if 'branch_name' not in self.changed_data:
            return 'Default Branch'
        return self.cleaned_data.get('branch_name')

    def clean_username(self):
        username = self.cleaned_data.get('username', None)
        is_available = User.objects.check_username_availability(username=username)
        if not is_available:
            raise ValidationError(_('A user with that username already exists.'))
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', None)
        is_available = User.objects.check_email_availability(email=email)
        if not is_available:
            raise ValidationError(_('This email is belong to another user.'))
        return email
