from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType

from pulsifi.models import Report


class VerifiedListFilter(admin.SimpleListFilter):
    title = "Verified"
    parameter_name = "verified"

    def lookups(self, request, model_admin):
        return ("1", "Is Verified"), ("0", "Is Not Verified")

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(verified=True)
        if self.value() == "0":
            return queryset.filter(verified=False)


class VisibleListFilter(admin.SimpleListFilter):
    title = "Visibility"
    parameter_name = "visible"

    def lookups(self, request, model_admin):
        return ("1", "Visible"), ("0", "Not Visible")

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(is_active=True)
        if self.value() == "0":
            return queryset.filter(is_active=False)


class GroupListFilter(admin.SimpleListFilter):
    title = "Group"
    parameter_name = "group"

    def lookups(self, request, model_admin):
        return ((str(group.id), str(group.name)) for group in Group.objects.all())

    def queryset(self, request, queryset):
        group_id = self.value()
        if group_id:
            return queryset.filter(groups=group_id)
        return queryset


class StaffListFilter(admin.SimpleListFilter):
    title = "Staff Member Status"
    parameter_name = "is_staff"

    def lookups(self, request, model_admin):
        return ("1", "Is Staff Member"), ("0", "Not Staff Member")

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(is_staff=True)
        if self.value() == "0":
            return queryset.filter(is_staff=False)


class ReportedObjectTypeListFilter(admin.SimpleListFilter):
    title = "Reported Object Type"
    parameter_name = "content_type"

    def lookups(self, request, model_admin):
        # noinspection PyProtectedMember
        return [(content_type.id, str(content_type).split(" ")[-1]) for content_type in ContentType.objects.filter(**Report._meta.get_field("_content_type")._limit_choices_to)]

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(is_staff=True)
        if self.value() == "0":
            return queryset.filter(is_staff=False)


class AssignedStaffListFilter(admin.SimpleListFilter):
    title = "Assigned Staff Member"
    parameter_name = "assigned_staff_member"

    def lookups(self, request, model_admin):
        # noinspection PyProtectedMember
        return [(user.id, str(user)) for user in get_user_model().objects.filter(**Report._meta.get_field("assigned_staff_member")._limit_choices_to)]

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(is_staff=True)
        if self.value() == "0":
            return queryset.filter(is_staff=False)


class CategoryListFilter(admin.SimpleListFilter):
    title = "Category"
    parameter_name = "category"

    def lookups(self, request, model_admin):
        return [category_choice for category_choice in Report.category_choices]

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(is_staff=True)
        if self.value() == "0":
            return queryset.filter(is_staff=False)


class StatusListFilter(admin.SimpleListFilter):
    title = "Status"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return [status_choice for status_choice in Report.status_choices]

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(is_staff=True)
        if self.value() == "0":
            return queryset.filter(is_staff=False)
