from allauth.account.models import EmailAddress
from avatar.models import Avatar
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Count

from pulsifi.models import Pulse, Reply, Report


# TODO: add better inheritance to remove duplicated code (e.g. user generated content inline)


class _Base_Inline_Config:
    classes = ["collapse"]
    extra = 0


class _Base_GenericInline(GenericTabularInline):
    ct_field = "_content_type"
    ct_fk_field = "_object_id"


class _Base_Pulse_Inline_Config(_Base_Inline_Config):
    model = Pulse


class _Base_Reply_Inline_Config(_Base_Inline_Config):
    model = Reply


class _Base_Report_Inline_Config(_Base_Inline_Config):
    model = Report


class EmailAddress_Inline(_Base_Inline_Config, admin.TabularInline):  # TODO: fix Email_Address_Inline_Admin formatting
    model = EmailAddress


class Avatar_Inline(_Base_Inline_Config, admin.TabularInline):
    model = Avatar


class Created_Pulse_Inline(_Base_Pulse_Inline_Config, admin.TabularInline):
    fk_name = "creator"
    verbose_name = "Created Pulse"
    autocomplete_fields = ["liked_by", "disliked_by"]
    readonly_fields = ["display_likes", "display_dislikes"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _likes=Count("liked_by", distinct=True),
            _dislikes=Count("disliked_by", distinct=True),
        )
        return queryset

    @admin.display(description="Number of likes", ordering="_likes")  # TODO: admin range filter on likes & dislikes field
    def display_likes(self, obj: Reply):
        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._likes

    @admin.display(description="Number of dislikes", ordering="_dislikes")
    def display_dislikes(self, obj: Reply):
        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._dislikes


class Liked_Pulse_Inline(_Base_Inline_Config, admin.StackedInline):
    model = Pulse.liked_by.through
    verbose_name = "Liked Pulse"
    readonly_fields = ["display_likes", "display_dislikes"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _likes=Count("pulse__liked_by", distinct=True),
            _dislikes=Count("pulse__disliked_by", distinct=True),
        )
        return queryset

    @admin.display(description="Number of likes", ordering="_likes")  # TODO: admin range filter on likes & dislikes field
    def display_likes(self, obj: Reply):
        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._likes

    @admin.display(description="Number of dislikes", ordering="_dislikes")
    def display_dislikes(self, obj: Reply):
        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._dislikes

    def has_add_permission(self, request, obj):
        return False


class Disliked_Pulse_Inline(_Base_Inline_Config, admin.StackedInline):
    model = Pulse.disliked_by.through
    verbose_name = "Disliked Pulse"
    readonly_fields = ["display_likes", "display_dislikes"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _likes=Count("pulse__liked_by", distinct=True),
            _dislikes=Count("pulse__disliked_by", distinct=True),
        )
        return queryset

    @admin.display(description="Number of likes", ordering="_likes")  # TODO: admin range filter on likes & dislikes field
    def display_likes(self, obj: Reply):
        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._likes

    @admin.display(description="Number of dislikes", ordering="_dislikes")
    def display_dislikes(self, obj: Reply):
        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._dislikes

    def has_add_permission(self, request, obj):
        return False


class Created_Reply_Inline(_Base_Reply_Inline_Config, admin.TabularInline):
    fk_name = "creator"
    verbose_name = "Created Reply"
    verbose_name_plural = "Created Replies"
    autocomplete_fields = ["liked_by", "disliked_by"]
    readonly_fields = ["display_likes", "display_dislikes"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _likes=Count("liked_by", distinct=True),
            _dislikes=Count("disliked_by", distinct=True),
        )
        return queryset

    @admin.display(description="Number of likes", ordering="_likes")  # TODO: admin range filter on likes & dislikes field
    def display_likes(self, obj: Reply):
        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._likes

    @admin.display(description="Number of dislikes", ordering="_dislikes")
    def display_dislikes(self, obj: Reply):
        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._dislikes


class Liked_Reply_Inline(_Base_Inline_Config, admin.StackedInline):
    model = Reply.liked_by.through
    verbose_name = "Liked Reply"
    verbose_name_plural = "Liked Replies"
    readonly_fields = ["display_likes", "display_dislikes"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _likes=Count("reply__liked_by", distinct=True),
            _dislikes=Count("reply__disliked_by", distinct=True),
        )
        return queryset

    @admin.display(description="Number of likes", ordering="_likes")  # TODO: admin range filter on likes & dislikes field
    def display_likes(self, obj: Reply):
        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._likes

    @admin.display(description="Number of dislikes", ordering="_dislikes")
    def display_dislikes(self, obj: Reply):
        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._dislikes

    def has_add_permission(self, request, obj):
        return False


class Disliked_Reply_Inline(_Base_Inline_Config, admin.StackedInline):
    model = Reply.disliked_by.through
    verbose_name = "Disliked Reply"
    verbose_name_plural = "Disliked Replies"
    readonly_fields = ["display_likes", "display_dislikes"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _likes=Count("reply__liked_by", distinct=True),
            _dislikes=Count("reply__disliked_by", distinct=True),
        )
        return queryset

    @admin.display(description="Number of likes", ordering="_likes")  # TODO: admin range filter on likes & dislikes field
    def display_likes(self, obj: Reply):
        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._likes

    @admin.display(description="Number of dislikes", ordering="_dislikes")
    def display_dislikes(self, obj: Reply):
        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._dislikes

    def has_add_permission(self, request, obj):
        return False


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
        if request.user.is_superuser and super().has_add_permission(request, obj):
            return True
        return False


class Direct_Reply_Inline(_Base_Reply_Inline_Config, _Base_GenericInline):
    fk_name = "reply_set"
    verbose_name = "Direct Reply"
    verbose_name_plural = "Direct Replies"
    autocomplete_fields = ["liked_by", "disliked_by"]
    fields = ["creator", "message", "liked_by", "disliked_by", "display_likes", "display_dislikes", "original_pulse", "visible"]
    readonly_fields = ["original_pulse", "display_likes", "display_dislikes"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _likes=Count("liked_by", distinct=True),
            _dislikes=Count("disliked_by", distinct=True),
        )
        return queryset

    @admin.display(description="Number of likes", ordering="_likes")  # TODO: admin range filter on likes & dislikes field
    def display_likes(self, obj: Reply):
        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._likes

    @admin.display(description="Number of dislikes", ordering="_dislikes")
    def display_dislikes(self, obj: Reply):
        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._dislikes
