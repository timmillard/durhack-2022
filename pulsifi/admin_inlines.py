from allauth.account.models import EmailAddress
from avatar.models import Avatar
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Count, QuerySet

from pulsifi.models import Pulse, Reply, Report, User


class _Base_Inline_Config:
    classes = ["collapse"]
    extra = 0


class _Base_GenericInline(GenericTabularInline):
    ct_field = "_content_type"
    ct_fk_field = "_object_id"


class _Base_Display_Likes_Dislikes_Inline_Config(_Base_Inline_Config):
    readonly_fields = ["display_likes", "display_dislikes"]

    @admin.display(description="Number of likes", ordering="_likes")
    def display_likes(self, obj: Pulse | Reply):
        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._likes

    @admin.display(description="Number of dislikes", ordering="_dislikes")
    def display_dislikes(self, obj: Pulse | Reply):
        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._dislikes


class _Created_Display_Likes_Dislikes_Inline(_Base_Display_Likes_Dislikes_Inline_Config, admin.StackedInline):
    fk_name = "creator"
    autocomplete_fields = ["liked_by", "disliked_by"]

    def get_queryset(self, request):
        queryset: QuerySet = super().get_queryset(request)

        queryset = queryset.annotate(
            _likes=Count("liked_by", distinct=True),
            _dislikes=Count("disliked_by", distinct=True),
        )

        return queryset


class _Related_Display_Likes_Dislikes_Inline(_Base_Display_Likes_Dislikes_Inline_Config, admin.TabularInline):
    def _get_queryset(self, request, model: str):
        if model not in ("pulse", "reply"):
            raise ValueError(f"The argument: model must be on of pulse, reply. {model} is not a valid option.")

        queryset: QuerySet = super().get_queryset(request)

        queryset = queryset.annotate(
            _likes=Count(f"{model}__liked_by", distinct=True),
            _dislikes=Count(f"{model}__disliked_by", distinct=True),
        )

        return queryset

    def has_add_permission(self, request, obj):
        return False


class _Related_Pulse_Display_Likes_Dislikes_Inline(_Related_Display_Likes_Dislikes_Inline):
    @admin.display(description="Date created", ordering="_date_time_created")
    def display_date_time_created(self, obj: Pulse.liked_by.through | Pulse.disliked_by.through):
        return obj.reply.date_time_created.strftime("%d %b %Y %I:%M:%S %p")

    def get_queryset(self, request):
        return super()._get_queryset(request, "pulse")

    def get_fields(self, request, obj=None):
        fields: list[str] = super().get_fields(request, obj)

        if "display_original_pulse" in fields:
            fields.remove("display_original_pulse")

        return fields


class _Related_Reply_Display_Likes_Dislikes_Inline(_Related_Display_Likes_Dislikes_Inline):
    @admin.display(description="Date created", ordering="_date_time_created")
    def display_date_time_created(self, obj: Reply.liked_by.through | Reply.disliked_by.through):
        return obj.reply.date_time_created.strftime("%d %b %Y %I:%M:%S %p")

    @admin.display(description="Original Pulse")
    def display_original_pulse(self, obj: Reply.liked_by.through | Reply.disliked_by.through):
        return obj.reply.original_pulse

    def get_queryset(self, request):
        return super()._get_queryset(request, "reply")


class _Base_Pulse_Inline_Config(_Base_Inline_Config):
    model = Pulse


class _Base_Reply_Inline_Config(_Base_Inline_Config):
    model = Reply

    @admin.display(description="Original Pulse")
    def display_original_pulse(self, obj: Reply):
        return obj.original_pulse


class _Base_Report_Inline_Config(_Base_Inline_Config):
    model = Report


class EmailAddress_Inline(_Base_Inline_Config, admin.TabularInline):
    model = EmailAddress


class Avatar_Inline(_Base_Inline_Config, admin.TabularInline):
    model = Avatar
    fields = ["avatar", "primary", "date_uploaded"]


class Created_Pulse_Inline(_Base_Pulse_Inline_Config, _Created_Display_Likes_Dislikes_Inline):
    verbose_name = "Created Pulse"
    fieldsets = [
        (None, {
            "fields": ["message", ("visible", "display_date_time_created")]
        }),
        ("Likes & Dislikes", {
            "fields": [("liked_by", "display_likes"), ("disliked_by", "display_dislikes")]
        })
    ]

    @admin.display(description="Date created", ordering="_date_time_created")
    def display_date_time_created(self, obj: Pulse):
        return obj.date_time_created.strftime("%d %b %Y %I:%M:%S %p")

    def get_readonly_fields(self, request, obj=None):
        readonly_fields: list[str] = super().get_readonly_fields(request, obj)

        if "display_date_time_created" not in readonly_fields:
            readonly_fields.append("display_date_time_created")

        return readonly_fields


class Liked_Pulse_Inline(_Related_Pulse_Display_Likes_Dislikes_Inline):
    model = Pulse.liked_by.through
    verbose_name = "Liked Pulse"


class Disliked_Pulse_Inline(_Related_Pulse_Display_Likes_Dislikes_Inline):
    model = Pulse.disliked_by.through
    verbose_name = "Disliked Pulse"


class Created_Reply_Inline(_Base_Reply_Inline_Config, _Created_Display_Likes_Dislikes_Inline):
    verbose_name = "Created Reply"
    verbose_name_plural = "Created Replies"
    fieldsets = [
        (None, {
            "fields": ["message", ("visible", "display_date_time_created")]
        }),
        ("Replied Content", {
            "fields": [("_content_type", "_object_id"), "display_original_pulse"]
        }),
        ("Likes & Dislikes", {
            "fields": [("liked_by", "display_likes"), ("disliked_by", "display_dislikes")],
            "classes": ["collapse"]
        })
    ]

    @admin.display(description="Date created", ordering="_date_time_created")
    def display_date_time_created(self, obj: Reply):
        return obj.date_time_created.strftime("%d %b %Y %I:%M:%S %p")

    def get_readonly_fields(self, request, obj=None):
        readonly_fields: list[str] = super().get_readonly_fields(request, obj)

        if "display_date_time_created" not in readonly_fields:
            readonly_fields.append("display_date_time_created")

        if "display_original_pulse" not in readonly_fields:
            readonly_fields.append("display_original_pulse")

        return readonly_fields


class Liked_Reply_Inline(_Related_Reply_Display_Likes_Dislikes_Inline):
    model = Reply.liked_by.through
    verbose_name = "Liked Reply"
    verbose_name_plural = "Liked Replies"


class Disliked_Reply_Inline(_Related_Reply_Display_Likes_Dislikes_Inline):
    model = Reply.disliked_by.through
    verbose_name = "Disliked Reply"
    verbose_name_plural = "Disliked Replies"


class About_Object_Report_Inline(_Base_Report_Inline_Config, _Base_GenericInline):
    fk_name = "reported_object"
    verbose_name = "Report About This Object"
    verbose_name_plural = "Reports About This Object"


class Submitted_Report_Inline(_Base_Report_Inline_Config, admin.TabularInline):
    fk_name = "reporter"
    verbose_name = "Submitted Report"


class Staff_Assigned_Report_Inline(_Base_Report_Inline_Config, admin.TabularInline):
    fk_name = "assigned_staff_member"
    verbose_name = "Staff Assigned Report"

    def has_add_permission(self, request, obj):
        user: User = request.user

        if user.is_superuser and super().has_add_permission(request, obj):
            return True

        return False


class Direct_Reply_Inline(_Base_Reply_Inline_Config, _Base_Display_Likes_Dislikes_Inline_Config, _Base_GenericInline):
    fk_name = "reply_set"
    verbose_name = "Direct Reply"
    verbose_name_plural = "Direct Replies"
    fields = ["creator", "message", "liked_by", "disliked_by", "display_likes", "display_dislikes", "display_original_pulse", "visible"]
    autocomplete_fields = ["liked_by", "disliked_by"]

    def get_queryset(self, request):
        queryset: QuerySet = super().get_queryset(request)

        queryset = queryset.annotate(
            _likes=Count("liked_by", distinct=True),
            _dislikes=Count("disliked_by", distinct=True),
        )

        return queryset

    def get_readonly_fields(self, request, obj=None):
        readonly_fields: list[str] = super().get_readonly_fields(request, obj)

        if "display_original_pulse" not in readonly_fields:
            readonly_fields.append("display_original_pulse")

        return readonly_fields
