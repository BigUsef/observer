from secrets import token_hex
from uuid import uuid4

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, Group as BaseGroup
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _

from authentication.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = RegexValidator(
        regex='^[a-z_]*$',
        message=_('Enter a valid Username consisting of lowercase letters or underscores.'),
        code='invalid'
    )

    # region Model Attribute
    username = models.CharField(
        _('username'),
        max_length=50,
        unique=True,
        db_index=True,
        help_text='Required. 50 characters or fewer. only contain lowercase letters or underscores.',
        validators=[username_validator],
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
        db_index=True,
        help_text='Required. valid email must be provided to use when contact with user.',
        error_messages={
            'unique': _('A user with that email address already exists.'),
        },
    )

    first_name = models.CharField('first name', max_length=30, blank=True)
    last_name = models.CharField('last name', max_length=90, blank=True)

    token = models.CharField("auth token", max_length=50, db_index=True, blank=True)
    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        'active status',
        default=True,
        help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'
    )
    date_joined = models.DateTimeField('date joined', auto_now_add=True)
    is_verified = models.BooleanField(
        'Has Verified Account',
        default=False,
        help_text='Designates whether this user has completed sign up process.'
    )
    # endregion

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    class Meta:
        db_table = 'auth_user'
        verbose_name = _('user')
        verbose_name_plural = _('authentication Accounts')

    def __str__(self) -> str:
        return self.full_name if self.full_name else str(self.username)

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    @property
    def full_name(self) -> str:
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def update_last_login(self, commit: bool = True) -> None:
        """
        update last_login field with now datetime and save update
        :parameter commit: if i want to override save behavior
        :return: None
        """
        self.last_login = timezone.now()
        if commit:
            self.save()

    def generate_token(self, commit: bool = True) -> str:
        """
        generate API token key and save it for this instance
        :parameter commit: if i want to override save behavior
        :return: string contain the new generated token key
        """
        self.token = token_hex(25)
        if User.objects.check_token_availability(self.token):
            if commit:
                self.save()
            return self.token
        else:
            return self.generate_token(commit=commit)

    def send_email(self, subject: str, template, context: dict, **kwargs) -> None:
        """
        send email to user based on user email address.
        :param subject: email subject
        :param template: email template path
        :param context: dict object represent template context
        """
        html_message = render_to_string(template_name=template, context=context)
        plain_message = kwargs.pop('message') if 'message' in kwargs else strip_tags(html_message)
        send_mail(
            subject=subject,
            message=plain_message,
            recipient_list=[self.email],
            html_message=html_message,
            **kwargs
        )

    def send_activation_email(self) -> None:
        """
        set user information in cash and send activation email to user
        """
        cache_id = uuid4()
        user_obj = {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email
        }
        # save user data on cache and set valid timeout to 1 day
        cache.set(cache_id, user_obj, timeout=86400)

        # send email
        self.send_email(
            subject='Welcome on board',
            template='email/account_activation.html',
            context={
                'code': cache_id,
                'name': self.full_name if self.full_name else self.username
            },
            message='',
            from_email='verification@observer.com'
        )


class Group(BaseGroup):
    class Meta:
        proxy = True
        app_label = 'authentication'
