"""
    Admin configurations for models in pulsifi app.
"""
import logging
from typing import Sequence, Type

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count, QuerySet
from django.forms import BaseModelForm
from rangefilter.filters import DateTimeRangeFilter

from .admin_filters import AssignedModeratorListFilter, CategoryListFilter, CreatedPulsesListFilter, CreatedRepliesListFilter, DirectRepliesListFilter, DislikesListFilter, GroupListFilter, HasReportAboutObjectListFilter, LikesListFilter, RepliedObjectTypeListFilter, ReportedObjectTypeListFilter, StaffListFilter, StatusListFilter, UserContentVisibleListFilter, UserVerifiedListFilter, UserVisibleListFilter
from .admin_inlines import About_Object_Report_Inline, Avatar_Inline, Created_Pulse_Inline, Created_Reply_Inline, Direct_Reply_Inline, Disliked_Pulse_Inline, Disliked_Reply_Inline, EmailAddress_Inline, Liked_Pulse_Inline, Liked_Reply_Inline, Moderator_Assigned_Report_Inline, Submitted_Report_Inline, _Base_Report_Inline_Config
from .models import Pulse, Reply, Report, User

# admin.site.login = login_required(admin.site.login)
admin.site.site_header = "Pulsifi Administration"
admin.site.site_title = "Pulsifi Admin"
admin.site.index_title = "Whole Site Overview"
admin.site.empty_value_display = "- - - - -"

logger = logging.getLogger(__name__)


class _Custom_Base_Admin(admin.ModelAdmin):
    """
        Custom base admin display configuration for all models in pulsifi app, that
        customises how querysets are deleted.
    """

    def delete_queryset(self, request, queryset: QuerySet[Pulse | Reply | Report]) -> None:
        """
            Overrides original queryset deletion by calling delete() on each
            object individually (rather than the bulk delete command), so that
            every objects custom delete() method can be executed (which will
            just mark each object as not visible, rather than actually deleting
            it from the database).
        """

        for obj in queryset:
            obj.delete()


class _Display_Date_Time_Created_Admin(_Custom_Base_Admin):
    """
        Base admin display configuration for models in the pulsifi app, that
        adds the functionality to display the date_time_created field with
        custom datetime formatting.
    """

    date_hierarchy = "_date_time_created"
    readonly_fields = ("display_date_time_created",)
    list_filter = (("_date_time_created", DateTimeRangeFilter),)

    @admin.display(description="Date created", ordering="_date_time_created")
    def display_date_time_created(self, obj: Pulse | Reply | Report) -> str:
        """
            Returns the custom formatted string representation of the
            date_time_created field, to be displayed on the admin page.
        """

        return obj.date_time_created.strftime("%d %b %Y %I:%M:%S %p")


class _User_Content_Admin(_Display_Date_Time_Created_Admin):
    """
        Base admin display configuration for User_Generated_Content models in
        the pulsifi app, that adds the functionality to display common fields &
        provide custom display configurations on the list, create & update
        pages.
    """

    list_display = (
        "creator",
        "message",
        "display_likes",
        "display_dislikes",
        "display_direct_replies_count",
        "display_full_depth_replies_count",
        "visible"
    )
    actions = None
    search_fields = ("creator", "message", "liked_by", "disliked_by")
    autocomplete_fields = ("liked_by", "disliked_by")
    search_help_text = "Search for a creator, message content or liked/disliked by user"
    list_editable = ("visible",)
    inlines = (Direct_Reply_Inline, About_Object_Report_Inline)
    list_display_links = ("creator", "message")

    def get_queryset(self, request) -> QuerySet[Pulse | Reply]:
        """
            Return a QuerySet of all :model:`pulsifi.user` model instances that
            can be edited by the admin site. This is used by changelist_view.

            Adds the calculated annotated fields likes, dislikes &
            direct_replies to the queryset.
        """

        queryset: QuerySet[Pulse | Reply] = super().get_queryset(request)

        queryset = queryset.annotate(
            _likes=Count("liked_by", distinct=True),
            _dislikes=Count("disliked_by", distinct=True),
            _direct_replies=Count("reply_set", distinct=True)
        )

        return queryset

    @admin.display(description="Number of likes", ordering="_likes")
    def display_likes(self, obj: Pulse | Reply) -> int:
        """
            Returns the number of likes this User_Generated_Content has, to be
            displayed on the admin page.
        """

        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._likes

    @admin.display(description="Number of dislikes", ordering="_dislikes")
    def display_dislikes(self, obj: Pulse | Reply) -> int:
        """
            Returns the number of dislikes this User_Generated_Content has, to
            be displayed on the admin page.
        """

        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._dislikes

    @admin.display(description="Number of direct replies", ordering="_direct_replies")
    def display_direct_replies_count(self, obj: Pulse | Reply) -> int:
        """
            Returns the number of :model:`pulsifi.reply` objects for this
            User_Generated_Content, to be displayed on the admin page.
        """

        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._direct_replies

    @admin.display(description="Number of full depth replies")
    def display_full_depth_replies_count(self, obj: Pulse | Reply) -> int:
        """
            Returns the number of :model:`pulsifi.reply` objects that are
            within the tree of this User_Generated_Content's
            children/children's children etc, to be displayed on the admin
            page.
        """

        return len(obj.full_depth_replies)

    def get_readonly_fields(self, request, obj: Pulse | Reply = None) -> Sequence[str]:
        """
            Adds the necessary readonly fields to the parent class's set of
            readonly_fields, only if they don't already exist.
        """

        readonly_fields: set[str] = set(super().get_readonly_fields(request, obj))

        readonly_fields.update(
            "display_likes",
            "display_dislikes",
            "display_direct_replies_count",
            "display_full_depth_replies_count"
        )

        return tuple(readonly_fields)

    def get_list_filter(self, request) -> Sequence[Type[admin.ListFilter]]:
        """
            Adds the necessary list_filters to the parent class's set of
            list_filters, only if they don't already exist.
        """

        list_filter: set[Type[admin.ListFilter]] = set(super().get_list_filter(request))

        list_filter.update(
            (
                UserContentVisibleListFilter,
                HasReportAboutObjectListFilter,
                LikesListFilter,
                DislikesListFilter,
                DirectRepliesListFilter
            )
        )

        return tuple(list_filter)

    def get_inlines(self, request, obj: Pulse | Reply) -> Sequence[Type[admin.options.InlineModelAdmin]]:
        """
            Adds the necessary inlines to the parent class's set of inlines,
            only if they don't already exist.
        """

        inlines: set[Type[admin.options.InlineModelAdmin]] = set(super().get_inlines(request, obj))

        try:
            Report._meta.get_field("assigned_moderator").default()

        except get_user_model().DoesNotExist:
            return tuple([inline for inline in inlines if not issubclass(inline, _Base_Report_Inline_Config)])
        else:
            return tuple(inlines)


@admin.register(Pulse)
class Pulse_Admin(_User_Content_Admin):
    """
        Admin display configuration for :model:`pulsifi.pulse` models, that
        adds the functionality to provide custom display configurations on the
        list, create & update pages.
    """

    fieldsets = (
        (None, {
            "fields": ("creator", "message")
        }),
        ("Likes & Dislikes", {
            "fields": (
                ("liked_by", "display_likes"),
                ("disliked_by", "display_dislikes")
            ),
            "classes": ("collapse",)
        }),
        ("Replies", {
            "fields": (
                ("display_direct_replies_count",
                 "display_full_depth_replies_count")
            )
        }),
        (None, {
            "fields": ("visible", "display_date_time_created")
        })
    )

    def get_list_display(self, request) -> Sequence[str]:
        """
            Removes the necessary list_display fields from the parent class's
            set of list_display fields, if they already exist when they
            shouldn't.
        """

        list_display: list[str] = list(super().get_list_display(request))

        try:
            list_display.remove("display_original_pulse")
        except KeyError:
            pass

        return tuple(list_display)

    def get_fieldsets(self, request, obj: Pulse = None) -> Sequence[tuple[str | None, dict[str, Sequence[str | tuple[str, ...]]]]]:
        """
            Removes/adds the necessary fieldsets fields from the parent class's
            fieldsets configuration, if they already exist when they shouldn't,
            or if they don't exist when they should.
        """

        fieldsets: Sequence[tuple[(str | None), dict[str, Sequence[str | tuple[str, ...]]]]] = super().get_fieldsets(request, obj)

        if obj is None:
            fields_2 = list(fieldsets[2][1]["fields"])
            try:
                fields_2.remove("display_date_time_created")
            except KeyError:
                pass
            else:
                fieldsets[2][1]["fields"] = tuple(fields_2)

            fields_1 = list(fieldsets[1][1]["fields"])
            if ("liked_by", "display_likes") in fields_1 and ("disliked_by", "display_dislikes") in fields_1:
                liked_index = fields_1.index(("liked_by", "display_likes"))
                fields_1.remove(("liked_by", "display_likes"))
                fields_1.remove(("disliked_by", "display_dislikes"))
                if ("liked_by", "disliked_by") not in fields_1:
                    fields_1.insert(liked_index, ("liked_by", "disliked_by"))
                fieldsets[1][1]["fields"] = tuple(fields_1)

            temp_fieldsets = list(fieldsets)
            try:
                temp_fieldsets.remove(
                    ("Replies", {"fields": [("display_direct_replies_count", "display_full_depth_replies_count")]})
                )
            except KeyError:
                pass
            else:
                fieldsets = tuple(temp_fieldsets)

        return fieldsets


@admin.register(Reply)
class Reply_Admin(_User_Content_Admin):
    """
        Admin display configuration for :model:`pulsifi.reply` models, that
        adds the functionality to provide custom display configurations on the
        list, create & update pages.
    """

    fieldsets = (
        (None, {
            "fields": ("creator", "message")
        }),
        ("Replied Content", {
            "fields": (
                ("_content_type", "_object_id"),
                "display_original_pulse"
            )
        }),
        ("Likes", {
            "fields": (
                ("liked_by", "display_likes"),
                ("disliked_by", "display_dislikes")
            ),
            "classes": ("collapse",)
        }),
        ("Replies", {
            "fields": ((
                "display_direct_replies_count",
                "display_full_depth_replies_count"
            ))
        }),
        (None, {
            "fields": ("visible", "display_date_time_created")
        })
    )

    @admin.display(description="Original Pulse")
    def display_original_pulse(self, obj: Reply) -> Pulse:
        """
            Returns the single :model:`pulsifi.pulse` object instance that is the
            highest parent object in the tree of :model:`pulsifi.pulse` &
            :model:`pulsifi.reply` objects that this :model:`pulsifi.reply`
            object is within, to be displayed on the admin page.
        """

        return obj.original_pulse

    def get_fieldsets(self, request, obj: Reply = None) -> Sequence[tuple[str | None, dict[str, Sequence[str | tuple[str, ...]]]]]:
        """
            Removes/adds the necessary fieldsets fields from the parent class's
            fieldsets configuration, if they already exist when they shouldn't,
            or if they don't exist when they should.
        """

        fieldsets: Sequence[tuple[(str | None), dict[str, Sequence[str | tuple[str, ...]]]]] = super().get_fieldsets(request, obj)

        if obj is None:
            fields_1 = list(fieldsets[1][1]["fields"])
            try:
                fields_1.remove("display_original_pulse")
            except KeyError:
                pass
            else:
                fieldsets[1][1]["fields"] = tuple(fields_1)

            fields_3 = list(fieldsets[3][1]["fields"])
            try:
                fields_3.remove("display_date_time_created")
            except KeyError:
                pass
            else:
                fieldsets[3][1]["fields"] = fields_3

            fields_2 = list(fieldsets[2][1]["fields"])
            if ("liked_by", "display_likes") in fields_2 and ("disliked_by", "display_dislikes") in fields_2:
                liked_index = fields_2.index(("liked_by", "display_likes"))
                fields_2.remove(("liked_by", "display_likes"))
                fields_2.remove(("disliked_by", "display_dislikes"))
                if ("liked_by", "disliked_by") not in fields_2:
                    fields_2.insert(liked_index, ("liked_by", "disliked_by"))
                fieldsets[2][1]["fields"] = tuple(fields_2)

            temp_fieldsets = list(fieldsets)
            try:
                temp_fieldsets.remove(
                    ("Replies", {"fields": [("display_direct_replies_count", "display_full_depth_replies_count")]})
                )
            except KeyError:
                pass
            else:
                fieldsets = tuple(temp_fieldsets)

        else:
            fields_2 = list(fieldsets[2][1]["fields"])
            if ("liked_by", "display_likes") not in fields_2 and ("disliked_by", "display_dislikes") not in fields_2:
                fields_2.append(("liked_by", "display_likes"))
                fields_2.append(("disliked_by", "display_dislikes"))
                fieldsets[2][1]["fields"] = tuple(fields_2)

        return fieldsets

    def get_list_display(self, request) -> Sequence[str]:
        """
            Removes the necessary list_display fields from the parent class's
            set of list_display fields, if they don't exist when they should.
        """

        list_display: list[str] = list(super().get_list_display(request))

        if "display_original_pulse" not in list_display:
            if "display_dislikes" in list_display:
                list_display.insert(
                    list_display.index("display_dislikes"),
                    "display_original_pulse"
                )
            else:
                list_display.append("display_original_pulse")

        return tuple(list_display)

    def get_list_filter(self, request) -> Sequence[Type[admin.ListFilter]]:
        """
            Adds the necessary list_filters to the parent class's set of
            list_filters, only if they don't already exist.
        """

        list_filter: set[Type[admin.ListFilter]] = set(super().get_list_filter(request))

        list_filter.add(RepliedObjectTypeListFilter)

        return tuple(list_filter)

    def get_readonly_fields(self, request, obj: Reply = None) -> Sequence[str]:
        """
            Adds the necessary readonly fields to the parent class's set of
            readonly_fields, only if they don't already exist.
        """

        readonly_fields: set[str] = set(super().get_readonly_fields(request, obj))

        readonly_fields.add("display_original_pulse")

        return tuple(readonly_fields)


@admin.register(Report)
class Report_Admin(_Display_Date_Time_Created_Admin):
    """
        Admin display configuration for :model:`pulsifi.report` models, that
        adds the functionality to provide custom display configurations on the
        list, create & update pages.
    """

    fields = (
        "reporter",
        ("_content_type", "_object_id"),
        "reason",
        "category",
        ("assigned_moderator", "status"),
        "display_date_time_created"
    )
    list_display = ("display_report", "reporter", "category", "status")
    list_display_links = ("display_report",)
    list_editable = ("reporter", "category", "status")
    readonly_fields = ("display_report", "display_date_time_created")
    search_fields = (
        "reporter",
        "_content_type",
        "reason",
        "category",
        "assigned_moderator",
        "status"
    )
    search_help_text = "Search for a reporter, reported object type, reason, category, assigned moderator or status"

    @admin.display(description="Report", ordering=["_content_type", "_object_id"])
    def display_report(self, obj: Report) -> str:
        """
            Returns the stringified version of the given
            :model:`pulsifi.report` object instance, to be displayed on the
            list admin page.
        """

        return str(obj)[:18]

    def get_fields(self, request, obj: Report = None) -> Sequence[str | tuple[str, ...]]:
        """
            Removes/adds the necessary fields from the parent class's fields
            configuration, if they already exist when they shouldn't, or if
            they don't exist when they should.
        """

        fields: list[str | tuple[str, ...]] = list(super().get_fields(request, obj))
        if obj is None:
            if ("assigned_moderator", "status") in fields:
                status_index = fields.index(("assigned_moderator", "status"))
                fields.remove(("assigned_moderator", "status"))
                if "status" not in fields:
                    fields.insert(status_index, "status")

            try:
                fields.remove("display_date_time_created")
            except KeyError:
                pass

        else:
            if "status" in fields:
                status_index = fields.index("status")
                fields.remove("status")
                if ("assigned_moderator", "status") not in fields:
                    fields.insert(status_index, ("assigned_moderator", "status"))

            if "display_date_time_created" not in fields:
                if ("assigned_moderator", "status") in fields:
                    fields.insert(
                        fields.index(("assigned_moderator", "status")),
                        "display_date_time_created"
                    )
                else:
                    fields.append("display_date_time_created")

        return tuple(fields)

    def get_list_filter(self, request) -> Sequence[Type[admin.ListFilter]]:
        """
            Adds the necessary list_filters to the parent class's set of
            list_filters, only if they don't already exist.
        """

        list_filter: set[Type[admin.ListFilter]] = set(super().get_list_filter(request))

        list_filter.update(
            (
                ReportedObjectTypeListFilter,
                AssignedModeratorListFilter,
                CategoryListFilter,
                StatusListFilter
            )
        )

        return tuple(list_filter)

    def has_add_permission(self, request) -> bool:
        """ Prevents creation of this object if no moderators exist. """

        try:
            Report._meta.get_field("assigned_moderator").default()
        except get_user_model().DoesNotExist:
            return False
        else:
            return True


@admin.register(get_user_model())
class User_Admin(BaseUserAdmin):
    """
        Admin display configuration for :model:`pulsifi.user` models, that
        adds the functionality to provide custom display configurations on the
        list, create & update pages.
    """

    date_hierarchy = "date_joined"
    filter_horizontal = ["user_permissions"]
    actions = None
    fieldsets = (
        (None, {
            "fields": (
                ("username", "email"),
                "bio",
                ("verified", "is_active"),
                "following"
            )
        }),
        ("Authentication", {
            "fields": (
                "display_date_joined",
                "display_last_login",
                "password"
            ),
            "classes": ("collapse",)
        }),
        ("Permissions", {
            "fields": (
                "groups",
                "user_permissions",
                "is_staff",
                "is_superuser"
            ),
            "classes": ("collapse",)
        })
    )
    add_fieldsets = (
        (None, {
            "fields": (("username", "email"), ("password1", "password2"))
        }),
        ("Extra", {
            "fields": ("bio", ("verified", "is_active"), "following"),
            "classes": ("collapse",)
        }),
        ("Permissions", {
            "fields": (
                "groups",
                "user_permissions",
                "is_staff",
                "is_superuser"
            ),
            "classes": ("collapse",)
        })
    )
    inlines = (
        EmailAddress_Inline,
        Avatar_Inline,
        Created_Pulse_Inline,
        Liked_Pulse_Inline,
        Disliked_Pulse_Inline,
        Created_Reply_Inline,
        Liked_Reply_Inline,
        Disliked_Reply_Inline,
        About_Object_Report_Inline,
        Submitted_Report_Inline,
        Moderator_Assigned_Report_Inline
    )
    list_display = (
        "display_username",
        "email",
        "verified",
        "is_staff",
        "is_active",
        "display_pulses",
        "display_replies"
    )
    list_display_links = ("display_username",)
    list_editable = ("email", "verified", "is_staff", "is_active")
    list_filter = (
        UserVerifiedListFilter,
        StaffListFilter,
        GroupListFilter,
        HasReportAboutObjectListFilter,
        UserVisibleListFilter,
        ("bio", admin.EmptyFieldListFilter),
        CreatedPulsesListFilter,
        CreatedRepliesListFilter,
        ("date_joined", DateTimeRangeFilter),
        ("last_login", DateTimeRangeFilter)
    )
    autocomplete_fields = (
        "following",
        "groups",
        "liked_pulse_set",
        "disliked_pulse_set",
        "liked_reply_set",
        "disliked_reply_set"
    )
    readonly_fields = (
        "display_username",
        "password",
        "display_date_joined",
        "display_last_login",
        "display_pulses",
        "display_replies"
    )
    search_fields = ("username", "email", "bio")
    search_help_text = "Search for a username, email address or bio"

    def get_queryset(self, request) -> QuerySet[User]:
        """
            Return a QuerySet of all :model:`pulsifi.user` model instances that
            can be edited by the admin site. This is used by changelist_view.

            Adds the calculated annotated fields pulses & replies to the
            queryset.
        """

        queryset: QuerySet[User] = super().get_queryset(request)

        queryset = queryset.annotate(
            _pulses=Count("created_pulse_set", distinct=True),
            _replies=Count("created_reply_set", distinct=True)
        )

        return queryset

    @admin.display(description="Number of created Pulses", ordering="_pulses")
    def display_pulses(self, obj: User) -> int:
        """
            Returns the number of :model:`pulsifi.pulse` objects this user has
            created, to be displayed on the admin page.
        """

        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._pulses

    @admin.display(description="Number of created Replies", ordering="_replies")
    def display_replies(self, obj: User) -> int:
        """
            Returns the number of :model:`pulsifi.reply` objects this user has
            created, to be displayed on the admin page.
        """

        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._replies

    @admin.display(description="Username", ordering="username")
    def display_username(self, obj: User) -> str:
        """
            Returns the username of this user, from the stringified version of
            the given :model:`pulsifi.user` object instance, to be displayed on
            the list admin page.
        """

        return str(obj)

    @admin.display(description="Date joined", ordering="date_joined")
    def display_date_joined(self, obj: User) -> str:
        """
            Returns the custom formatted string representation of the
            date_joined field, to be displayed on the admin page.
        """

        return obj.date_joined.strftime("%d %b %Y %I:%M:%S %p")

    @admin.display(description="Last login", ordering="last_login")
    def display_last_login(self, obj: User) -> str:
        """
            Returns the custom formatted string representation of the
            last_login field, to be displayed on the admin page.
        """

        return obj.last_login.strftime("%d %b %Y %I:%M:%S %p")

    def get_form(self, *args, **kwargs) -> Type[BaseModelForm]:
        """
            Return a Form class for use in the admin add view. This is used by
            add_view and change_view.

            Changes the labels on the form to remove unnecessary clutter.
        """

        kwargs.update(
            {
                "labels": {"password": "Hashed password string"},
                "help_texts": {"is_active": None}
            }
        )
        return super().get_form(*args, **kwargs)

    def get_inlines(self, request, obj: User) -> Sequence[Type[admin.options.InlineModelAdmin]]:
        """
            Adds the necessary inlines to the parent class's set of inlines,
            only if they don't already exist.
        """

        inlines: set[Type[admin.options.InlineModelAdmin]] = set(super().get_inlines(request, obj))

        if obj is None:
            inlines.discard(EmailAddress_Inline)

        try:
            Report._meta.get_field("assigned_moderator").default()
        except get_user_model().DoesNotExist:
            inlines = {inline for inline in inlines if not issubclass(inline, _Base_Report_Inline_Config)}

        return tuple(inlines)

    def delete_queryset(self, request, queryset: QuerySet[User]) -> None:
        """
            Overrides original queryset deletion by calling delete() on each
            object individually (rather than the bulk delete command), so that
            every objects custom delete() method can be executed (which will
            just mark each object as not visible, rather than actually deleting
            it from the database).
        """

        for obj in queryset:
            obj.delete()
