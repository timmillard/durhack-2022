"""
    Admin configurations for models in pulsifi app.
"""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count

from .admin_filters import AssignedStaffListFilter, CategoryListFilter, GroupListFilter, RepliedObjectTypeListFilter, ReportedObjectTypeListFilter, StaffListFilter, StatusListFilter, UserContentVisibleListFilter, UserVisibleListFilter, VerifiedListFilter
from .admin_inlines import About_Object_Report_Inline, Avatar_Inline, Created_Pulse_Inline, Created_Reply_Inline, Direct_Reply_Inline, Disliked_Pulse_Inline, Disliked_Reply_Inline, EmailAddress_Inline, Liked_Pulse_Inline, Liked_Reply_Inline, Staff_Assigned_Report_Inline, Submitted_Report_Inline, _Base_Report_Inline_Config
from .models import Pulse, Reply, Report, User

admin.site.site_header = "Pulsifi Administration"
admin.site.site_title = "Pulsifi Admin"
admin.site.index_title = "Whole Site Overview"
admin.site.empty_value_display = "- - - - -"


# TODO: Number of pulses range filter for user, number of replies range filter for user, reported filter for user, number of likes & dislikes range filter

class _Custom_Base_Admin(admin.ModelAdmin):
    def delete_queryset(self, request, queryset):
        obj: Pulse | Reply | Report | User
        for obj in queryset:
            obj.delete()


class _Display_Date_Time_Created_Admin(_Custom_Base_Admin):
    date_hierarchy = "_date_time_created"
    readonly_fields = ["display_date_time_created"]

    @admin.display(description="Date created", ordering="_date_time_created")
    def display_date_time_created(self, obj: Pulse | Reply | Report):
        return obj.date_time_created.strftime("%d %b %Y %I:%M:%S %p")


class _User_Content_Admin(_Display_Date_Time_Created_Admin):
    list_display = [
        "creator",
        "message",
        "display_likes",
        "display_dislikes",
        "display_direct_replies_count",
        "display_full_depth_replies_count",
        "visible"
    ]
    search_fields = ["creator", "message", "liked_by", "disliked_by"]
    autocomplete_fields = ["liked_by", "disliked_by"]
    list_filter = [UserContentVisibleListFilter]
    search_help_text = "Search for a creator, message content or liked/disliked by user"
    list_editable = ["visible"]
    inlines = [Direct_Reply_Inline, About_Object_Report_Inline]
    list_display_links = ["creator", "message"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        queryset = queryset.annotate(
            _likes=Count("liked_by", distinct=True),
            _dislikes=Count("disliked_by", distinct=True),
            _direct_replies=Count("reply_set", distinct=True)
        )

        return queryset

    @admin.display(description="Number of likes", ordering="_likes")
    def display_likes(self, obj: Pulse | Reply):
        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._likes

    @admin.display(description="Number of dislikes", ordering="_dislikes")
    def display_dislikes(self, obj: Pulse | Reply):
        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._dislikes

    @admin.display(description="Number of direct replies")
    def display_direct_replies_count(self, obj: Pulse | Reply):
        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._direct_replies

    @admin.display(description="Number of full depth replies")
    def display_full_depth_replies_count(self, obj: Pulse | Reply):
        return len(obj.full_depth_replies)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [readonly_field for readonly_field in super().get_readonly_fields(request, obj)]

        if "display_likes" not in readonly_fields:
            readonly_fields.append("display_likes")
        if "display_dislikes" not in readonly_fields:
            readonly_fields.append("display_dislikes")
        if "display_direct_replies_count" not in readonly_fields:
            readonly_fields.append("display_direct_replies_count")
        if "display_full_depth_replies_count" not in readonly_fields:
            readonly_fields.append("display_full_depth_replies_count")

        return readonly_fields

    def get_inlines(self, request, obj):
        inlines = super().get_inlines(request, obj)

        try:
            Report._meta.get_field("assigned_staff_member").default()

        except get_user_model().DoesNotExist:
            inlines = [inline for inline in inlines if not issubclass(inline, _Base_Report_Inline_Config)]

        return inlines


@admin.register(Pulse)
class Pulse_Admin(_User_Content_Admin):
    fieldsets = [
        (None, {
            "fields": ["creator", "message"]
        }),
        ("Likes & Dislikes", {
            "fields": [("liked_by", "display_likes"), ("disliked_by", "display_dislikes")],
            "classes": ["collapse"]
        }),
        ("Replies", {
            "fields": [("display_direct_replies_count", "display_full_depth_replies_count")]
        }),
        (None, {
            "fields": ["visible", "display_date_time_created"]
        })
    ]

    def get_list_display(self, request):
        list_display: list[str] = super().get_list_display(request)

        if "display_original_pulse" in list_display:
            list_display.remove("display_original_pulse")

        return list_display

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        if not obj:
            if "display_date_time_created" in fieldsets[2][1]["fields"]:
                fieldsets[2][1]["fields"].remove("display_date_time_created")

            if fieldsets[1][1]["fields"][0] == ("liked_by", "display_likes") and fieldsets[1][1]["fields"][1] == ("disliked_by", "display_dislikes"):
                fieldsets[1][1]["fields"] = [("liked_by", "disliked_by")]
            elif ("liked_by", "display_likes") in fieldsets[1][1]["fields"]:
                fieldsets[1][1]["fields"][fieldsets[1][1]["fields"].index(("liked_by", "display_likes"))] = "liked_by"
            elif ("disliked_by", "display_dislikes") in fieldsets[1][1]["fields"]:
                fieldsets[1][1]["fields"][fieldsets[1][1]["fields"].index(("disliked_by", "display_dislikes"))] = "disliked_by"

        return fieldsets


@admin.register(Reply)
class Reply_Admin(_User_Content_Admin):
    fieldsets = [
        (None, {
            "fields": ["creator", "message"]
        }),
        ("Replied Content", {
            "fields": [("_content_type", "_object_id"), "display_original_pulse"]
        }),
        ("Likes", {
            "fields": [("liked_by", "display_likes"), ("disliked_by", "display_dislikes")],
            "classes": ["collapse"]
        }),
        ("Replies", {
            "fields": [("display_direct_replies_count", "display_full_depth_replies_count")]
        }),
        (None, {
            "fields": ["visible", "display_date_time_created"]
        })
    ]

    @admin.display(description="Original Pulse")
    def display_original_pulse(self, obj: Reply):
        return obj.original_pulse

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        if not obj:
            if "display_original_pulse" in fieldsets[1][1]["fields"]:
                fieldsets[1][1]["fields"].remove("display_original_pulse")

            if "display_date_time_created" in fieldsets[3][1]["fields"]:
                fieldsets[3][1]["fields"].remove("display_date_time_created")

            if fieldsets[2][1]["fields"][0] == ("liked_by", "display_likes") and fieldsets[2][1]["fields"][1] == ("disliked_by", "display_dislikes"):
                fieldsets[2][1]["fields"] = [("liked_by", "disliked_by")]
            elif ("liked_by", "display_likes") in fieldsets[2][1]["fields"]:
                fieldsets[2][1]["fields"][fieldsets[2][1]["fields"].index(("liked_by", "display_likes"))] = "liked_by"
            elif ("disliked_by", "display_dislikes") in fieldsets[2][1]["fields"]:
                fieldsets[2][1]["fields"][fieldsets[2][1]["fields"].index(("disliked_by", "display_dislikes"))] = "disliked_by"

        elif ("liked_by", "display_likes") not in fieldsets[2][1]["fields"] and ("disliked_by", "display_dislikes") not in fieldsets[2][1]["fields"]:
            fieldsets[2][1]["fields"] = [("liked_by", "display_likes"), ("disliked_by", "display_dislikes")]

        return fieldsets

    def get_list_display(self, request):
        list_display: list[str] = super().get_list_display(request)

        if "display_original_pulse" not in list_display:
            list_display.insert(4, "display_original_pulse")

        return list_display

    def get_list_filter(self, request):
        list_filter: list = super().get_list_filter(request)

        if RepliedObjectTypeListFilter not in list_filter:
            list_filter.append(RepliedObjectTypeListFilter)

        return list_filter

    def get_readonly_fields(self, request, obj=None):
        readonly_fields: list[str] = super().get_readonly_fields(request, obj)

        if "display_original_pulse" not in readonly_fields:
            readonly_fields.append("display_original_pulse")

        return readonly_fields


@admin.register(Report)
class Report_Admin(_Display_Date_Time_Created_Admin):
    fields = [
        "reporter",
        ("_content_type", "_object_id"),
        "reason",
        "category",
        ("assigned_staff_member", "status"),
        "display_date_time_created"
    ]
    list_display = ["display_report", "reporter", "category", "status"]
    list_display_links = ["display_report"]
    list_editable = ["reporter", "category", "status"]
    list_filter = [ReportedObjectTypeListFilter, AssignedStaffListFilter, CategoryListFilter, StatusListFilter]
    readonly_fields = ["display_report", "display_date_time_created"]
    search_fields = ["reporter", "_content_type", "reason", "category", "assigned_staff_member", "status"]
    search_help_text = "Search for a reporter, reported object type, reason, category, assigned staff member or status"

    @admin.display(description="Report", ordering=["_content_type", "_object_id"])
    def display_report(self, obj: Report):
        return str(obj)[:18]

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not obj:
            if ("assigned_staff_member", "status") in fields:
                fields[fields.index(("assigned_staff_member", "status"))] = "status"

            if "display_date_time_created" in fields:
                fields.remove("display_date_time_created")
        return fields

    def has_add_permission(self, request):
        try:
            Report._meta.get_field("assigned_staff_member").default()
        except get_user_model().DoesNotExist:
            return False
        return True


@admin.register(get_user_model())
class User_Admin(BaseUserAdmin):
    date_hierarchy = "date_joined"
    filter_horizontal = ["user_permissions"]
    fieldsets = [
        (None, {
            "fields": [("username", "email"), "bio", ("verified", "is_active"), "following"]
        }),
        ("Authentication", {
            "fields": ["display_date_joined", "display_last_login", "password"],
            "classes": ["collapse"]
        }),
        ("Permissions", {
            "fields": ["groups", "user_permissions", "is_staff", "is_superuser"],
            "classes": ["collapse"]
        })
    ]
    add_fieldsets = [
        (None, {
            "fields": [("username", "email"), ("password1", "password2")]
        }),
        ("Extra", {
            "fields": ["bio", ("verified", "is_active"), "following"],
            "classes": ["collapse"]
        }),
        ("Permissions", {
            "fields": ["groups", "user_permissions", "is_staff", "is_superuser"],
            "classes": ["collapse"]
        })
    ]
    inlines = [
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
        Staff_Assigned_Report_Inline
    ]
    list_display = ["display_username", "email", "verified", "is_staff", "is_active"]
    list_display_links = ["display_username"]
    list_editable = ["email", "verified", "is_staff", "is_active"]
    list_filter = [VerifiedListFilter, StaffListFilter, GroupListFilter, UserVisibleListFilter, ("bio", admin.EmptyFieldListFilter)]
    autocomplete_fields = ["following", "groups", "liked_pulse_set", "disliked_pulse_set", "liked_reply_set", "disliked_reply_set"]
    readonly_fields = ["display_username", "password", "display_date_joined", "display_last_login"]
    search_fields = ["username", "email", "bio"]
    search_help_text = "Search for a username, email address or bio"

    @admin.display(description="Username", ordering="username")
    def display_username(self, obj: User):
        return str(obj)

    @admin.display(description="Date joined", ordering="date_joined")
    def display_date_joined(self, obj: User):
        return obj.date_joined.strftime("%d %b %Y %I:%M:%S %p")

    @admin.display(description="Last login", ordering="last_login")
    def display_last_login(self, obj: User):
        return obj.last_login.strftime("%d %b %Y %I:%M:%S %p")

    def get_form(self, *args, **kwargs):
        kwargs.update(
            {
                "labels": {"password": "Hashed password string"},
                "help_texts": {"is_active": None}
            }
        )
        return super().get_form(*args, **kwargs)

    def get_inlines(self, request, obj):
        inlines = super().get_inlines(request, obj)

        if not obj:
            inlines = [inline for inline in inlines if inline != EmailAddress_Inline]

        try:
            Report._meta.get_field("assigned_staff_member").default()
        except get_user_model().DoesNotExist:
            inlines = [inline for inline in inlines if not issubclass(inline, _Base_Report_Inline_Config)]

        return inlines
