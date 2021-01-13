from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm, UsernameField
from django.utils.translation import ugettext_lazy as _

from authentication.models import User


class UserCreationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = 'username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff',
        field_classes = {'username': UsernameField}

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.check_email_availability(email=email):
            raise forms.ValidationError(_('This email is belong to another user.'))
        return email
