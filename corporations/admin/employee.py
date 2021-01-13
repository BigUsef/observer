from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django_reverse_admin import ReverseModelAdmin

from corporations.models import Employee

User = get_user_model()


@admin.register(Employee)
class EmployeeModelAdmin(ReverseModelAdmin):
    list_display = '__str__', 'facility', 'is_chief', 'account_verification',
    list_filter = 'is_chief',
    search_fields = 'user__username', 'user__first_name', 'user__last_name', 'facility__name',
    raw_id_fields = 'facility',

    inline_type = 'stacked'
    inline_reverse = [
        ('user', {
            'fields': ['username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login'],
            'show_change_link': True,
            'readonly_fields': ['date_joined', 'last_login'],
            'has_delete_permission': lambda request, obj: False,
        }),
    ]

    def account_verification(self, obj):
        return obj.user.is_verified

    account_verification.short_description = _('Verified')
    account_verification.boolean = True

    def save_model(self, request, obj, form, change):
        if not change:
            random_password = User.objects.make_random_password(length=9)
            obj.user.set_password(random_password)
            obj.user.save()
        return super().save_model(request, obj, form, change)
