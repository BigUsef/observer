from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _

from authentication.admin.forms import UserCreationForm
from authentication.models import User, Group, BaseGroup

admin.site.site_header = 'Supervisors Dashboard'
admin.site.site_title = 'Dashboard'
admin.site.index_title = 'Welcome in Observer Supervisors Dashboard'
admin.site.unregister(BaseGroup)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password', 'token')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Account status'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        (_('Permissions'), {
            'fields': ('groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('is_verified', 'date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff'),
        }),
    )
    readonly_fields = 'token', 'is_superuser', 'date_joined', 'last_login', 'is_verified',

    add_form = UserCreationForm
    list_display = '__str__', 'username', 'is_staff', 'is_active', 'date_joined',
    list_filter = 'is_staff', 'is_active', 'groups',
    search_fields = 'username', 'first_name', 'last_name', 'email',
    ordering = 'first_name',


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = 'id', 'name'
