"""
    Models in pulsifi app.
"""

import logging
from abc import abstractmethod
from typing import Final

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, Group
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Manager, Q
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from tldextract import tldextract
from tldextract.tldextract import ExtractResult

from .models_utils import Custom_Base_Model, get_random_staff_member
from .validators import HTML5EmailValidator, ReservedNameValidator, validate_confusables, validate_confusables_email, validate_example_email, validate_free_email, validate_tld_email

logger = logging.getLogger(__name__)


class _Visible_Reportable_Model(Custom_Base_Model):
    """
        Base model that prevents objects from actually being deleted (making
        them invisible instead), as well as allowing all objects of this type
        to have reports made about them.
    """

    about_object_report_set = GenericRelation(
        "Report",
        content_type_field="_content_type",
        object_id_field="_object_id",
        related_query_name="reverse_parent_object",
        verbose_name="Reports About This Object"
    )
    """
        Provides a link to the set of all Report objects that link to this
        object.
    """

    class Meta:  # NOTE: This class is abstract (only used for inheritance) so should not be able to be instantiated or have a table made for it in the database
        abstract = True

    @property
    @abstractmethod
    def visible(self) -> bool:
        """
            Abstract declaration of field getter that MUST be implemented by
            child classes.
        """

        raise NotImplementedError

    @visible.setter
    @abstractmethod
    def visible(self, value: bool) -> None:
        """
            Abstract declaration of field setter that MUST be implemented by
            child classes.
        """

        raise NotImplementedError

    def delete(self, using: str = None, *args, **kwargs):
        self.visible = False
        self.save()

    def string_when_visible(self, string: str):
        """
            Returns the given string, or the given string but crossed out if
            this object is not visible.
        """

        if self.visible:
            return string
        return "".join(f"{char}\u0336" for char in string)  # NOTE: Adds the unicode strikethrough character between every character in the given string, to "cross out" the given string


class _User_Generated_Content_Model(_Visible_Reportable_Model):  # TODO: calculate time remaining based on engagement & creator follower count
    message = models.TextField("Message", blank=False, null=False)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Creator",
        related_name="created_%(class)s_set"
    )  # NOTE: Provides a link to the Profile that created this User_Generated_Content
    liked_by = models.ManyToManyField(  # TODO: prevent users from increasing the time by liking then unliking then reliking
        settings.AUTH_USER_MODEL,
        related_name="liked_%(class)s_set",
        blank=True
    )
    disliked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="disliked_%(class)s_set",
        blank=True
    )
    reply_set = GenericRelation(
        "Reply",
        content_type_field="_content_type",
        object_id_field="_object_id",
        verbose_name="Replies"
    )
    visible = models.BooleanField("Is visible?", default=True)
    _date_time_created = models.DateTimeField(
        "Creation Date & Time",
        auto_now=True
    )

    @property
    def date_time_created(self):
        return self._date_time_created

    class Meta:  # NOTE: This class is abstract (only used for inheritance) so should not be able to be instantiated or have a table made for it in the database
        abstract = True

    def __str__(self):
        return f"{self.creator}, {self.string_when_visible(self.message[:settings.MESSAGE_DISPLAY_LENGTH])}"

    def get_absolute_url(self):
        return f"""{reverse("pulsifi:feed")}?{type(self).__name__.lower()}={self.id}"""


class User(_Visible_Reportable_Model, AbstractUser):  # TODO: prevent new accounts with similar usernames (especially verified accounts)
    first_name = None  # make blank in save method
    last_name = None
    get_full_name = None
    get_short_name = None

    staff_assigned_report_set: Manager
    avatar_set: Manager
    disliked_pulse_set: Manager
    disliked_reply_set: Manager
    # noinspection SpellCheckingInspection
    emailaddress_set: Manager
    liked_pulse_set: Manager
    liked_reply_set: Manager
    logentry_set: Manager
    created_pulse_set: Manager
    created_reply_set: Manager
    submitted_report_set: Manager
    # noinspection SpellCheckingInspection
    socialaccount_set: Manager
    # noinspection SpellCheckingInspection
    staticdevice_set: Manager
    # noinspection SpellCheckingInspection
    totpdevice_set: Manager

    username = models.CharField(
        _("username"),
        max_length=30,
        unique=True,
        validators=[
            RegexValidator(
                r"^[\w.-]+\Z",
                _("Enter a valid username. This value may contain only letters, digits and ./_ characters.")
            ),
            ReservedNameValidator,
            validate_confusables
        ],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = models.EmailField(
        _("email address"),
        unique=True,
        validators=[
            HTML5EmailValidator,
            validate_free_email,
            validate_confusables_email,
            validate_tld_email,
            validate_example_email
        ],
        error_messages={
            "unique": _(f"That Email Address is already in use by another user."),
        },
    )
    bio = models.TextField(
        "Bio",
        max_length=200,
        blank=True
    )
    verified = models.BooleanField("Is verified?", default=False)  # TODO: Add verification process
    following = models.ManyToManyField(  # TODO: prevent follow self
        "self",
        symmetrical=False,
        related_name="followers",
        blank=True
    )
    is_staff = models.BooleanField(
        "Is a staff member?",
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_superuser = models.BooleanField(
        "Is a superuser?",
        default=False,
        help_text=_(
            "Designates that this user has all permissions without "
            "explicitly assigning them."
        ),
    )
    is_active = models.BooleanField(
        "Is visible?",
        default=True,
        help_text=_(
            "Designates whether this user is visible. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(
        _("date joined"),
        default=timezone.now,
        editable=False
    )
    last_login = models.DateTimeField(
        _("last login"),
        blank=True,
        null=True,
        editable=False
    )

    @property
    def visible(self):
        return self.is_active

    @visible.setter
    def visible(self, value):
        self.is_active = value

    class Meta:
        verbose_name = "User"

    def __str__(self):  # NOTE: Returns the User's username if they are still visible, otherwise returns the crossed out username
        return self.string_when_visible(f"@{self.username}")

    def clean(self):
        if self.is_superuser:
            self.is_staff = self.is_superuser

        if (get_user_model().objects.filter(username__icontains="pulsifi").count() > settings.PULSIFI_ADMIN_COUNT or not self.is_staff) and "pulsifi" in self.username.lower():
            raise ValidationError({"username": "That username is not allowed."}, code="invalid")

        if self.email.count("@") == 1:
            local: str
            whole_domain: str
            local, whole_domain = self.email.split("@", maxsplit=1)

            extracted_domain = tldextract.extract(whole_domain)

            local = local.replace(".", "")

            if "+" in local:
                local = local.split("+", maxsplit=1)[0]

            if extracted_domain.domain == "googlemail":
                extracted_domain = ExtractResult(subdomain=extracted_domain.subdomain, domain="gmail", suffix=extracted_domain.suffix)

            elif (get_user_model().objects.filter(username__icontains="pulsifi").count() > settings.PULSIFI_ADMIN_COUNT or not self.is_staff) and extracted_domain.domain == "pulsifi":
                raise ValidationError({"email": f"That Email Address cannot be used."}, code="invalid")

            self.email = "@".join([local, extracted_domain.fqdn])

        if EmailAddress.objects.filter(email=self.email).exclude(user=self).exists():
            raise ValidationError({"email": f"The Email Address: {self.email} is already in use by another user."}, code="unique")

        if self.verified:
            if self.id:
                if not self.emailaddress_set.filter(verified=True).exists():
                    raise ValidationError({"verified": "User cannot become verified without at least one verified email address."})
            else:
                raise ValidationError({"verified": "User cannot become verified without at least one verified email address."})

        super().clean()

    def save(self, *args, **kwargs):
        new = not self.id

        super().save(*args, **kwargs)

        if self.is_superuser:  # BUG: When User objects are saved on the admin page their groups will be reset to only the groups shown & added to the admin form. (This code will not correctly put superusers into the admin group) (Fix with m2m_changed signal that is sent here for normal saving & pinged when changed in admin)
            admin_group = Group.objects.filter(name="Admins").first()
            if admin_group and admin_group not in self.groups.all():
                self.groups.add(admin_group)

        if not new and not EmailAddress.objects.filter(email=self.email, user=self).exists():
            old_primary_email = EmailAddress.objects.filter(user=self, primary=True).first()
            if old_primary_email:
                old_primary_email.primary = False
                old_primary_email.save()

            EmailAddress.objects.create(email=self.email, user=self, primary=True)

    def get_absolute_url(self):
        return reverse("pulsifi:specific_account", kwargs={"username": self.username})


class Pulse(_User_Generated_Content_Model):  # TODO: disable the like & dislike buttons if profile already in set
    @property
    def full_depth_replies(self):
        return [reply for reply in Reply.objects.all() if reply.original_pulse == self]

    class Meta:
        verbose_name = "Pulse"

    def save(self, *args, **kwargs):
        self.full_clean()

        self_QS = Pulse.objects.filter(id=self.id)

        if self_QS.exists():
            if not self.visible and self_QS.get().visible:
                for reply in self.full_depth_replies:
                    reply.update(base_save=True, visible=False)

            elif self.visible and not self_QS.get().visible:
                for reply in self.full_depth_replies:
                    reply.update(base_save=True, visible=True)

        super().save(*args, **kwargs)


class Reply(_User_Generated_Content_Model):  # TODO: disable the like & dislike buttons if profile already in set
    _content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={"app_label": "pulsifi", "model__in": ("pulse", "reply")},
        verbose_name="Replied Content Type"
    )
    _object_id = models.PositiveIntegerField(verbose_name="Replied Content ID")
    replied_content = GenericForeignKey(ct_field="_content_type", fk_field="_object_id")

    @property
    def original_pulse(self):
        return self._find_original_pulse()

    class Meta:
        verbose_name = "Reply"
        verbose_name_plural = "Replies"
        indexes = [
            models.Index(fields=["_content_type", "_object_id"]),
        ]

    def __str__(self):
        return f"{self.creator}, {self.string_when_visible(self.message[:settings.MESSAGE_DISPLAY_LENGTH])} (For object - {self.replied_content})"

    def clean(self):
        try:
            if self._content_type not in ContentType.objects.filter(app_label="pulsifi", model__in=("pulse", "reply")):
                raise ValidationError({"_content_type": f"The Content Type: {self._content_type} is not one of the allowed options: Pulse, Reply."}, code="invalid")
        except ContentType.DoesNotExist:
            pass
        else:
            if (self._content_type == ContentType.objects.get(app_label="pulsifi", model="pulse") and self._object_id not in Pulse.objects.all().values_list("id", flat=True)) or (self._content_type == ContentType.objects.get(app_label="pulsifi", model="reply") and self._object_id not in Reply.objects.all().values_list("id", flat=True)):
                raise ValidationError("Replied content must be valid object")

        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()

        if not self.original_pulse.visible:
            self.visible = False

        self.base_save(clean=False, *args, **kwargs)

    def _find_original_pulse(self):
        if isinstance(self.replied_content, Pulse):
            return self.replied_content
        # noinspection PyProtectedMember
        return self.replied_content._find_original_pulse()


class Report(Custom_Base_Model):
    SPAM: Final = "SPM"
    SEXUAL: Final = "SEX"
    HATE: Final = "HAT"
    VIOLENCE: Final = "VIO"
    ILLEGAL_GOODS: Final = "IGL"
    BULLYING: Final = "BUL"
    INTELLECTUAL_PROPERTY: Final = "INP"
    SELF_INJURY: Final = "INJ"
    SCAM: Final = "SCM"
    FALSE_INFO: Final = "FLS"
    IN_PROGRESS: Final = "PR"
    REJECTED: Final = "RE"
    COMPLETED: Final = "CM"
    category_choices = [
        (SPAM, "Spam"),
        (SEXUAL, "Nudity or sexual activity"),
        (HATE, "Hate speech or symbols"),
        (VIOLENCE, "Violence or dangerous organisations"),
        (ILLEGAL_GOODS, "Sale of illegal or regulated goods"),
        (BULLYING, "Bullying or harassment"),
        (INTELLECTUAL_PROPERTY, "Intellectual property violation or impersonation"),
        (SELF_INJURY, "Suicide or self-injury"),
        (SCAM, "Scam or fraud"),
        (FALSE_INFO, "False or misleading information")
    ]
    status_choices = [
        (IN_PROGRESS, "In Progress"),
        (REJECTED, "Rejected"),
        (COMPLETED, "Completed")
    ]

    _content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={"app_label": "pulsifi", "model__in": ("user", "pulse", "reply")},
        verbose_name="Reported Object Type"
    )
    _object_id = models.PositiveIntegerField(verbose_name="Reported Object ID")
    reported_object = GenericForeignKey(ct_field="_content_type", fk_field="_object_id")
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Reporter",
        related_name="submitted_report_set"
    )
    assigned_staff_member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Assigned Staff Member",
        related_name="staff_assigned_report_set",
        limit_choices_to={"groups__name": "Moderators"},
        default=get_random_staff_member
    )
    reason = models.TextField("Reason")
    category = models.CharField(
        "Category",
        max_length=3,
        choices=category_choices
    )
    status = models.CharField(
        "Status",
        max_length=2,
        choices=status_choices,
        default=IN_PROGRESS
    )
    _date_time_created = models.DateTimeField(
        "Creation Date & Time",
        auto_now=True
    )

    @property
    def date_time_created(self):
        return self._date_time_created

    class Meta:
        verbose_name = "Report"
        indexes = [
            models.Index(fields=["_content_type", "_object_id"]),
        ]

    # noinspection PyFinal
    def __init__(self, *args, **kwargs):
        self.SPAM: Final = type(self).SPAM
        self.SEXUAL: Final = type(self).SEXUAL
        self.HATE: Final = type(self).HATE
        self.VIOLENCE: Final = type(self).VIOLENCE
        self.ILLEGAL_GOODS: Final = type(self).ILLEGAL_GOODS
        self.BULLYING: Final = type(self).BULLYING
        self.INTELLECTUAL_PROPERTY: Final = type(self).INTELLECTUAL_PROPERTY
        self.SELF_INJURY: Final = type(self).SELF_INJURY
        self.SCAM: Final = type(self).SCAM
        self.FALSE_INFO: Final = type(self).FALSE_INFO
        self.IN_PROGRESS: Final = type(self).IN_PROGRESS
        self.REJECTED: Final = type(self).REJECTED
        self.COMPLETED: Final = type(self).COMPLETED

        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"{self.reporter}, {self.get_category_display()}, {self.get_status_display()} (Assigned Staff Member - {self.assigned_staff_member})(For object - {self.reported_object})"

    def clean(self):
        try:
            if self._content_type not in ContentType.objects.filter(app_label="pulsifi", model__in=("user", "pulse", "reply")):
                raise ValidationError({"_content_type": f"The Content Type: {self._content_type} is not one of the allowed options: User, Pulse, Reply."}, code="invalid")

            if self._content_type == ContentType.objects.get(app_label="pulsifi", model="user") and self._object_id in get_user_model().objects.filter(Q(groups__name="Admins") | Q(id=self.reporter_id)).values_list("id", flat=True):
                raise ValidationError({"_object_id": f"The Object ID: {self._object_id} refers to an admin. Admins cannot be reported."}, code="invalid")

        except ContentType.DoesNotExist:
            pass

        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

        print(self.assigned_staff_member_id)
