from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class UsersConfig(AppConfig):
    name = 'authentication'
    verbose_name = _("Authentication and Authorization")
