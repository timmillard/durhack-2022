from django.contrib import admin
from django.contrib.auth.models import Group


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
