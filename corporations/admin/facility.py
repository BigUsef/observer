from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from corporations.admin.facility_forms import AddFacilityModelForm, BranchInlineForm
from corporations.models import Branch, Employee, Facility

User = get_user_model()


class BranchStackedInline(admin.TabularInline):
    model = Branch
    form = BranchInlineForm
    extra = 0

    def has_delete_permission(self, request, obj=None):
        # obj -> Facility instance
        if obj.branches.count() <= 1:
            return False
        else:
            return True


class EmployeeTabularInline(admin.StackedInline):
    model = Employee
    fields = 'username', 'full_name', 'is_chief',
    readonly_fields = 'username', 'full_name', 'is_chief',
    show_change_link = True

    def username(self, obj):
        return obj.user.username

    username.short_description = _('Username')

    def full_name(self, obj):
        return obj.user.full_name

    full_name.short_description = _('Full Name')

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Facility)
class FacilityModelAdmin(admin.ModelAdmin):
    list_display = 'name', 'branch_count', 'employee_count', 'created',
    exclude = 'branch_count', 'employee_count',
    inlines = BranchStackedInline, EmployeeTabularInline,
    list_filter = 'segment',
    search_fields = 'uid', 'name', 'branches__name',
    add_form = AddFacilityModelForm
    add_fieldsets = (
        (_('Facility'), {
            'classes': ('wide',),
            'fields': ('uid', 'name', 'segment'),
        }),
        (_('Main Branch'), {'fields': ('branch_name',)}),
        (_('Owner User'), {'fields': ('username', 'first_name', 'last_name', 'email',)}),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def get_inlines(self, request, obj):
        if obj is None:
            return list()
        return super().get_inlines(request, obj)

    def branch_count(self, instance) -> int:
        return instance.branches.count()

    branch_count.short_description = _("Branch Count")

    def employee_count(self, instance) -> int:
        return instance.staff.count()

    employee_count.short_description = _("Employee Count")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if not change:
            # create facility owner
            user = User.objects.create_user(
                username=form.cleaned_data.get('username', None),
                email=form.cleaned_data.get('email', None),
                first_name=form.cleaned_data.get('first_name', None),
                last_name=form.cleaned_data.get('last_name', None)
            )

            # create employee instance
            Employee.objects.create(user=user, facility=obj, is_chief=True)

            # create main branch
            Branch.objects.create(
                facility=obj,
                name=form.cleaned_data.get('branch_name', None),
                is_main=True
            )
