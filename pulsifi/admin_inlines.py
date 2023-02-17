"""
    Admin inlines for models in pulsifi app.
"""
from typing import Sequence

from allauth.account.models import EmailAddress
from avatar.models import Avatar
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Count, QuerySet

from pulsifi.models import Pulse, Reply, Report


class _Base_Inline_Config:
    """ Class to provide the base configuration values for all admin inlines. """

    classes = ["collapse"]
    extra = 0


class _Base_GenericInline(GenericTabularInline):
    """
        Base TabularInline with the connecting fields populated for every
        generic relation.
    """

    ct_field = "_content_type"
    ct_fk_field = "_object_id"


class _Base_User_Content_Inline_Config(_Base_Inline_Config):
    """
        Class to provide the base configuration values for
        User_Generated_Content admin inlines.
    """

    readonly_fields = (
        "display_likes",
        "display_dislikes",
        "display_direct_replies_count",
        "display_full_depth_replies_count"
    )

    @admin.display(description="Number of likes", ordering="_likes")
    def display_likes(self, obj: Pulse | Reply) -> int:
        """
            Returns the number of likes that this User_Generated_Content has,
            to be displayed within a User_Generated_Content inline on the admin
            page.
        """

        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._likes

    @admin.display(description="Number of dislikes", ordering="_dislikes")
    def display_dislikes(self, obj: Pulse | Reply) -> int:
        """
            Returns the number of dislikes that this User_Generated_Content
            has, to be displayed within a User_Generated_Content inline on the
            admin page.
        """

        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._dislikes

    @admin.display(description="Number of direct replies")
    def display_direct_replies_count(self, obj: Pulse | Reply) -> int:
        """
            Returns the number of direct :model:`pulsifi.reply` objects that
            this User_Generated_Content has, to be displayed within a
            User_Generated_Content inline on the admin page.
        """

        # noinspection PyUnresolvedReferences, PyProtectedMember
        return obj._direct_replies

    @admin.display(description="Number of full depth replies")
    def display_full_depth_replies_count(self, obj: Pulse | Reply) -> int:
        """
            Returns the number of total :model:`pulsifi.reply` objects that are
            within the tree of this instance's children/children's children
            etc, to be displayed within a User_Generated_Content inline on the
            admin page.
        """

        return len(obj.full_depth_replies)


class _Created_User_Content_Inline(_Base_User_Content_Inline_Config, admin.StackedInline):
    """
        Base StackedInline with the additional calculated fields for all
        Created_User_Content_Inlines (E.g. created pulses or created replies).
    """

    fk_name = "creator"
    autocomplete_fields = ("liked_by", "disliked_by")

    def get_queryset(self, request) -> QuerySet[Pulse | Reply]:
        """
            Return a QuerySet of all :model:`pulsifi.pulse` or
            :model:`pulsifi.reply` model instances that can be created/edited
            within this admin inline.

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


class _Related_User_Content_Inline(_Base_User_Content_Inline_Config, admin.TabularInline):
    """
        Base TabularInline with the additional calculated fields for all
        Related_User_Content_Inlines (E.g. liked pulses, disliked replies,
        etc).
    """

    def _get_queryset(self, request, model: str) -> QuerySet[Pulse | Reply]:
        """
            Return a QuerySet of all :model:`pulsifi.pulse` or
            :model:`pulsifi.reply` model instances that can be created/edited
            within this admin inline.

            Adds the calculated annotated fields likes, dislikes &
            direct_replies to the queryset.
        """

        if model not in ("pulse", "reply"):
            raise ValueError(f"The argument: model must be on of pulse, reply. {model} is not a valid option.")

        queryset: QuerySet[Pulse | Reply] = super().get_queryset(request)

        queryset = queryset.annotate(
            _likes=Count(f"{model}__liked_by", distinct=True),
            _dislikes=Count(f"{model}__disliked_by", distinct=True),
            _direct_replies=Count(f"{model}__reply_set", distinct=True)
        )

        return queryset

    def has_add_permission(self, request, obj: Pulse.liked_by.through | Pulse.disliked_by.through | Reply.liked_by.through | Reply.disliked_by.through) -> bool:  # HACK: Prevent from creating new content objects from within this type of inline, as validation/signals is/are not performed/sent correctly
        """
            Prevent creation of new content objects from within this type of
            inline, because validation/signals is/are not performed/sent
            correctly.
        """

        return False


class _Related_Pulse_Inline(_Related_User_Content_Inline):
    """
        Base TabularInline with the additional calculated fields for all
        Related_Pulse_Inlines (E.g. liked pulses, disliked pulses).
    """

    @admin.display(description="Date created", ordering="_date_time_created")
    def display_date_time_created(self, obj: Pulse.liked_by.through | Pulse.disliked_by.through) -> str:
        """
            Returns the custom formatted string representation of the
            date_time_created field, to be displayed within a
            Pulse_Related_User_Content inline on the admin page.
        """

        return obj.pulse.date_time_created.strftime("%d %b %Y %I:%M:%S %p")

    def get_queryset(self, request) -> QuerySet[Pulse]:
        """
            Return a QuerySet of all :model:`pulsifi.pulse` model instances
            that can be created/edited within this admin inline.

            Adds the calculated annotated fields from the base
            Related_User_Content_Inline with the correct model
            (:model:`pulsifi.pulse`).
        """

        return super()._get_queryset(request, "pulse")

    def get_fields(self, request, obj: Pulse.liked_by.through | Pulse.disliked_by.through = None) -> Sequence[str]:
        """
            Removes the necessary fields from the parent class's set of
            fields, only if they exist where they shouldn't.

            The display_original_pulse field should not be in the parent
            class's list of fields anyway, but it sometimes appears so must be
            removed to prevent an invalid reference.
        """

        fields: list[str] = list(super().get_fields(request, obj))

        try:
            fields.remove("display_original_pulse")  # HACK: Brute-force remove display_original_pulse field when it sometimes appears from the parent class's list of fields incorrectly
        except ValueError:
            pass

        return tuple(fields)


class _Related_Reply_Inline(_Related_User_Content_Inline):
    """
        Base TabularInline with the additional calculated fields for all
        Related_Reply_Inlines (E.g. liked replies, disliked replies).
    """

    @admin.display(description="Date created", ordering="_date_time_created")
    def display_date_time_created(self, obj: Reply.liked_by.through | Reply.disliked_by.through) -> str:
        """
            Returns the custom formatted string representation of the
            date_time_created field, to be displayed within a Related_Reply
            inline on the admin page.
        """

        return obj.reply.date_time_created.strftime("%d %b %Y %I:%M:%S %p")

    @admin.display(description="Original Pulse")
    def display_original_pulse(self, obj: Reply.liked_by.through | Reply.disliked_by.through) -> Pulse:
        """
            Returns the single :model:`pulsifi.pulse` object instance that is
            the highest parent object in the tree of :model:`pulsifi.pulse` &
            :model:`pulsifi.reply` objects that this :model:`pulsifi.reply`
            object is within, to be displayed within a Related_Reply inline on
            the admin page.
        """

        return obj.reply.original_pulse

    def get_queryset(self, request) -> QuerySet[Reply]:
        """
            Return a QuerySet of all :model:`pulsifi.reply` model instances
            that can be created/edited within this admin inline.

            Adds the calculated annotated fields from the base
            Related_User_Content_Inline with the correct model
            (:model:`pulsifi.reply`).
        """

        return super()._get_queryset(request, "reply")


class _Base_Pulse_Inline_Config(_Base_Inline_Config):
    """
        Class to provide the base configuration values for Pulse admin inlines.
        (Designates these admin inlines to use the :model:`pulsifi.pulse`
        model.)
    """

    model = Pulse


class _Base_Reply_Inline_Config(_Base_Inline_Config):
    """
        Class to provide the base configuration values for Reply admin inlines.
        (Designates these admin inlines to use the :model:`pulsifi.reply`
        model, as well as adding the additional original_pulse field.)
    """

    model = Reply

    @admin.display(description="Original Pulse")
    def display_original_pulse(self, obj: Reply) -> Pulse:
        """
            Returns the single :model:`pulsifi.pulse` object instance that is
            the highest parent object in the tree of :model:`pulsifi.pulse` &
            :model:`pulsifi.reply` objects that this :model:`pulsifi.reply`
            object is within, to be displayed within a Reply inline on the
            admin page.
        """

        return obj.original_pulse


class _Base_Report_Inline_Config(_Base_Inline_Config):
    """
        Class to provide the base configuration values for Report admin
        inlines. (Designates these admin inlines to use the
        :model:`pulsifi.report` model.)
    """

    model = Report


class EmailAddress_Inline(_Base_Inline_Config, admin.TabularInline):
    # noinspection SpellCheckingInspection
    """
        TabularInline providing the configuration values for how to display
        EmailAddress instances in this admin inline. (Designates this admin
        inline to use the :model:`account.emailaddress` model.)
    """

    model = EmailAddress


class Avatar_Inline(_Base_Inline_Config, admin.TabularInline):
    """
        TabularInline providing the configuration values for how to display
        Avatar instances in this admin inline. (Designates this admin
        inline to use the :model:`avatar.avatar` model, as well as selecting
        only a limited number of fields to show.)
    """

    model = Avatar
    fields = ["avatar", "primary", "date_uploaded"]


class Created_Pulse_Inline(_Base_Pulse_Inline_Config, _Created_User_Content_Inline):
    """
        StackedInline providing the configuration values for how to display
        Created_Pulses in this admin inline.
    """

    verbose_name = "Created Pulse"
    fieldsets = [
        (None, {
            "fields": ["message", ("visible", "display_date_time_created")]
        }),
        ("Likes & Dislikes", {
            "fields": [("liked_by", "display_likes"), ("disliked_by", "display_dislikes")]
        }),
        ("Replies", {
            "fields": [("display_direct_replies_count", "display_full_depth_replies_count")]
        }),
    ]

    @admin.display(description="Date created", ordering="_date_time_created")
    def display_date_time_created(self, obj: Pulse) -> str:
        """
            Returns the custom formatted string representation of the
            date_time_created field, to be displayed within a Created_Pulse
            inline on the admin page.
        """

        return obj.date_time_created.strftime("%d %b %Y %I:%M:%S %p")

    def get_readonly_fields(self, request, obj=None) -> Sequence[str]:
        """
            Adds the necessary readonly fields to the parent class's set of
            readonly_fields, only if they don't already exist.
        """

        readonly_fields: set[str] = set(super().get_readonly_fields(request, obj))

        readonly_fields.add("display_date_time_created")

        return tuple(readonly_fields)


class Liked_Pulse_Inline(_Related_Pulse_Inline):
    """
        TabularInline providing the configuration values for how to display
        Liked_Pulses in this admin inline. (Designates this admin inline to use
        the :model:`pulsifi.pulse` model.)
    """

    model = Pulse.liked_by.through
    verbose_name = "Liked Pulse"


class Disliked_Pulse_Inline(_Related_Pulse_Inline):
    """
        TabularInline providing the configuration values for how to display
        Disliked_Pulses in this admin inline. (Designates this admin inline to
        use the :model:`pulsifi.pulse` model.)
    """

    model = Pulse.disliked_by.through
    verbose_name = "Disliked Pulse"


class Created_Reply_Inline(_Base_Reply_Inline_Config, _Created_User_Content_Inline):
    """
        StackedInline providing the configuration values for how to display
        Created_Replies in this admin inline.
    """

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
        }),
        ("Replies", {
            "fields": [("display_direct_replies_count", "display_full_depth_replies_count")]
        }),
    ]

    @admin.display(description="Date created", ordering="_date_time_created")
    def display_date_time_created(self, obj: Reply) -> str:
        """
            Returns the custom formatted string representation of the
            date_time_created field, to be displayed within a Created_Reply
            inline on the admin page.
        """

        return obj.date_time_created.strftime("%d %b %Y %I:%M:%S %p")

    def get_readonly_fields(self, request, obj=None) -> Sequence[str]:
        """
            Adds the necessary readonly fields to the parent class's set of
            readonly_fields, only if they don't already exist.
        """

        readonly_fields: set[str] = set(super().get_readonly_fields(request, obj))

        readonly_fields.update(
            (
                "display_date_time_created",
                "display_original_pulse"
            )
        )

        return tuple(readonly_fields)


class Liked_Reply_Inline(_Related_Reply_Inline):
    """
        TabularInline providing the configuration values for how to display
        Liked_Replies in this admin inline. (Designates this admin inline to
        use the :model:`pulsifi.reply` model.)
    """

    model = Reply.liked_by.through
    verbose_name = "Liked Reply"
    verbose_name_plural = "Liked Replies"


class Disliked_Reply_Inline(_Related_Reply_Inline):
    """
        TabularInline providing the configuration values for how to display
        Disliked_Replies in this admin inline. (Designates this admin inline to
        use the :model:`pulsifi.reply` model.)
    """

    model = Reply.disliked_by.through
    verbose_name = "Disliked Reply"
    verbose_name_plural = "Disliked Replies"


class About_Object_Report_Inline(_Base_Report_Inline_Config, _Base_GenericInline):
    """
        GenericTabularInline providing the configuration values for how to
        display Reported_Parent_Objects in this admin inline. (Designates this
        admin inline to use the reported_object foreign key on the
        :model:`pulsifi.report` object instance.)
    """

    fk_name = "reported_object"
    verbose_name = "Report About This Object"
    verbose_name_plural = "Reports About This Object"


class Submitted_Report_Inline(_Base_Report_Inline_Config, admin.TabularInline):
    """
        TabularInline providing the configuration values for how to display
        Submitted_Reports in this admin inline. (Designates this admin inline
        to use the reporter foreign key on the :model:`pulsifi.user` object
        instance.)
    """

    fk_name = "reporter"
    verbose_name = "Submitted Report"


class Moderator_Assigned_Report_Inline(_Base_Report_Inline_Config, admin.TabularInline):
    """
        TabularInline providing the configuration values for how to display
        a moderator's Assigned_Reports in this admin inline. (Designates this
        admin inline to use the assigned_moderator foreign key on the
        :model:`pulsifi.report` object instance.)
    """

    fk_name = "assigned_moderator"
    verbose_name = "Moderator Assigned Report"


class Direct_Reply_Inline(_Base_Reply_Inline_Config, _Base_User_Content_Inline_Config, _Base_GenericInline):
    """
        GenericTabularInline providing the configuration values for how to
        display Direct_Replies in this admin inline.
    """

    fk_name = "reply_set"
    verbose_name = "Direct Reply"
    verbose_name_plural = "Direct Replies"
    fields = [
        "creator",
        "message",
        "liked_by",
        "disliked_by",
        "display_likes",
        "display_dislikes",
        "display_direct_replies_count",
        "display_full_depth_replies_count",
        "display_original_pulse",
        "visible"
    ]
    autocomplete_fields = ["liked_by", "disliked_by"]

    def get_queryset(self, request) -> QuerySet[Reply]:
        """
            Return a QuerySet of all :model:`pulsifi.reply` model instances
            that can be created/edited within this admin inline.

            Adds the calculated annotated fields likes, dislikes &
            direct_replies to the queryset.
        """

        queryset: QuerySet[Reply] = super().get_queryset(request)

        queryset = queryset.annotate(
            _likes=Count("liked_by", distinct=True),
            _dislikes=Count("disliked_by", distinct=True),
            _direct_replies=Count("reply_set", distinct=True)
        )

        return queryset

    def get_readonly_fields(self, request, obj: Reply = None) -> Sequence[str]:
        """
            Adds the necessary readonly fields to the parent class's set of
            readonly_fields, only if they don't already exist.
        """

        readonly_fields: set[str] = set(super().get_readonly_fields(request, obj))

        readonly_fields.add("display_original_pulse")

        return tuple(readonly_fields)
