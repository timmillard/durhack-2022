from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, PositiveIntegerField, QuerySet
from rangefilter.filters import NumericRangeFilter

from pulsifi.models import Pulse, Reply, Report, User


class UserVerifiedListFilter(admin.SimpleListFilter):
    title = "Verified"
    parameter_name = "verified"

    def lookups(self, request, model_admin):
        return ("1", "Is Verified"), ("0", "Is Not Verified")

    def queryset(self, request, queryset: QuerySet[User]):
        if self.value() == "1":
            return queryset.filter(verified=True)
        if self.value() == "0":
            return queryset.filter(verified=False)


class UserVisibleListFilter(admin.SimpleListFilter):
    title = "Visibility"
    parameter_name = "visible"

    def lookups(self, request, model_admin):
        return ("1", "Visible"), ("0", "Not Visible")

    def queryset(self, request, queryset: QuerySet[User]):
        if self.value() == "1":
            return queryset.filter(is_active=True)
        if self.value() == "0":
            return queryset.filter(is_active=False)


class GroupListFilter(admin.SimpleListFilter):
    title = "Group"
    parameter_name = "group"

    def lookups(self, request, model_admin):
        return ((str(group.id), str(group.name)) for group in Group.objects.all())

    def queryset(self, request, queryset: QuerySet[User]):
        group_id = self.value()
        if group_id is not None:
            return queryset.filter(groups=group_id)
        return queryset


class StaffListFilter(admin.SimpleListFilter):
    title = "Staff Member Status"
    parameter_name = "is_staff"

    def lookups(self, request, model_admin):
        return ("1", "Is Staff Member"), ("0", "Is Not Staff Member")

    def queryset(self, request, queryset: QuerySet[User]):
        if self.value() == "1":
            return queryset.filter(is_staff=True)
        if self.value() == "0":
            return queryset.filter(is_staff=False)


# noinspection PyAbstractClass
class CreatedPulsesListFilter(admin.ListFilter):
    def __new__(cls, request, params, model, model_admin):
        return NumericRangeFilter(
            PositiveIntegerField(verbose_name="Number of Created Pulses"),
            request,
            params,
            model,
            model_admin,
            field_path="_pulses",
        )


# noinspection PyAbstractClass
class CreatedRepliesListFilter(admin.ListFilter):
    def __new__(cls, request, params, model, model_admin):
        return NumericRangeFilter(
            PositiveIntegerField(verbose_name="Number of Created Replies"),
            request,
            params,
            model,
            model_admin,
            field_path="_replies",
        )


class ReportedObjectTypeListFilter(admin.SimpleListFilter):
    title = "Reported Object Type"
    parameter_name = "reported_object_type"

    def lookups(self, request, model_admin):
        # noinspection PyProtectedMember
        return [(str(content_type).split(" ")[-1].lower(), str(content_type).split(" ")[-1]) for content_type in ContentType.objects.filter(**Report._meta.get_field("_content_type")._limit_choices_to)]

    def queryset(self, request, queryset: QuerySet[Report]):
        content_type_name = self.value()
        if content_type_name is not None:
            # noinspection PyProtectedMember
            return queryset.filter(
                _content_type=ContentType.objects.filter(
                    **Report._meta.get_field("_content_type")._limit_choices_to
                ).filter(model=content_type_name).first()
            )
        return queryset


class AssignedStaffListFilter(admin.SimpleListFilter):
    title = "Assigned Staff Member"
    parameter_name = "assigned_staff_member"

    def lookups(self, request, model_admin):
        # noinspection PyProtectedMember
        return [(user.id, str(user)) for user in get_user_model().objects.filter(**Report._meta.get_field("assigned_staff_member")._limit_choices_to)]

    def queryset(self, request, queryset: QuerySet[Report]):
        user_id = self.value()
        if user_id is not None:
            return queryset.filter(assigned_staff_member_id=user_id)
        return queryset


class CategoryListFilter(admin.SimpleListFilter):
    title = "Category"
    parameter_name = "category"

    def lookups(self, request, model_admin):
        return [category_choice for category_choice in Report.category_choices]

    def queryset(self, request, queryset: QuerySet[Report]):
        category_choice = self.value()
        if category_choice is not None:
            return queryset.filter(category=category_choice)
        return queryset


class StatusListFilter(admin.SimpleListFilter):
    title = "Status"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return [status_choice for status_choice in Report.status_choices]

    def queryset(self, request, queryset: QuerySet[Report]):
        status_choice = self.value()
        if status_choice is not None:
            return queryset.filter(status=status_choice)
        return queryset


# noinspection PyAbstractClass
class LikesListFilter(admin.ListFilter):
    def __new__(cls, request, params, model, model_admin):
        return NumericRangeFilter(
            PositiveIntegerField(verbose_name="Number of Likes"),
            request,
            params,
            model,
            model_admin,
            field_path="_likes",
        )


# noinspection PyAbstractClass
class DislikesListFilter(admin.ListFilter):
    def __new__(cls, request, params, model, model_admin):
        return NumericRangeFilter(
            PositiveIntegerField(verbose_name="Number of Dislikes"),
            request,
            params,
            model,
            model_admin,
            field_path="_dislikes",
        )


class HasReportAboutObjectListFilter(admin.SimpleListFilter):
    title = "Number of Reports"
    parameter_name = "has_reports"

    def lookups(self, request, model_admin):
        return ("1", "Has Been Reported"), ("0", "Has Not Been Reported")

    def queryset(self, request, queryset: QuerySet[User | Pulse | Reply]):
        queryset = queryset.annotate(_reports=Count("about_object_report_set", distinct=True))
        if self.value() == "1":
            return queryset.filter(_reports__gt=0)
        if self.value() == "0":
            return queryset.filter(_reports=0)


class UserContentVisibleListFilter(admin.SimpleListFilter):
    title = "Visibility"
    parameter_name = "visible"

    def lookups(self, request, model_admin):
        return ("1", "Visible"), ("0", "Not Visible")

    def queryset(self, request, queryset: QuerySet[Pulse | Reply]):
        if self.value() == "1":
            return queryset.filter(visible=True)
        if self.value() == "0":
            return queryset.filter(visible=False)


class RepliedObjectTypeListFilter(admin.SimpleListFilter):
    title = "Replied Object Type"
    parameter_name = "replied_object_type"

    def lookups(self, request, model_admin):
        # noinspection PyProtectedMember
        return [(str(content_type).split(" ")[-1].lower(), str(content_type).split(" ")[-1]) for content_type in ContentType.objects.filter(**Reply._meta.get_field("_content_type")._limit_choices_to)]

    def queryset(self, request, queryset: QuerySet[Reply]):
        content_type_name = self.value()
        if content_type_name is not None:
            # noinspection PyProtectedMember
            return queryset.filter(
                _content_type=ContentType.objects.filter(
                    **Report._meta.get_field("_content_type")._limit_choices_to
                ).filter(model=content_type_name).first()
            )
        return queryset


# noinspection PyAbstractClass
class DirectRepliesListFilter(admin.ListFilter):
    def __new__(cls, request, params, model, model_admin):
        return NumericRangeFilter(
            PositiveIntegerField(verbose_name="Number of Direct Replies"),
            request,
            params,
            model,
            model_admin,
            field_path="_direct_replies",
        )
