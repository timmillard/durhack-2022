"""
    Models in pulsifi app.
"""

import logging
from abc import abstractmethod
from typing import Final

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .models_utils import Custom_Base_Model, get_random_staff_member
from .validators import HTML5EmailValidator, ReservedNameValidator, validate_confusables, validate_confusables_email, validate_free_email, validate_tld_email

logger = logging.getLogger(__name__)


class _Visible_Reportable_Model(Custom_Base_Model):
    """
        Base model that prevents objects from actually being deleted (making
        them invisible instead), as well as allowing all objects of this type
        to have reports made about them.
    """

    reports = GenericRelation(
        "Report",
        content_type_field="_content_type",
        object_id_field="_object_id",
        related_query_name="reverse_parent_object",
        verbose_name="Reports"
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
    visible = models.BooleanField("Visibility", default=True)
    message = models.TextField("Message")
    replies = GenericRelation(
        "Reply",
        content_type_field="_content_type",
        object_id_field="_object_id",
        verbose_name="Replies"
    )
    _date_time_created = models.DateTimeField(
        "Creation Date & Time",
        auto_now=True
    )

    @property
    def likes(self):
        return self.liked_by.count()

    @property
    def dislikes(self):
        return self.disliked_by.count()

    @property
    def date_time_created(self):
        return self._date_time_created

    @property
    @abstractmethod
    def liked_by(self) -> models.Manager:
        """
            Abstract declaration of field that MUST be implemented by child
            classes.
        """

        raise NotImplementedError

    @property
    @abstractmethod
    def disliked_by(self) -> models.Manager:
        """
            Abstract declaration of field that MUST be implemented by child
            classes.
        """

        raise NotImplementedError

    class Meta:  # NOTE: This class is abstract (only used for inheritance) so should not be able to be instantiated or have a table made for it in the database
        abstract = True

    def __str__(self):
        return self.string_when_visible(self.message[:settings.MESSAGE_DISPLAY_LENGTH])

    def like(self, user: "User"):  # TODO: prevent users from increasing the time by liking then unliking then reliking
        if self.disliked_by.filter(id=user.id).exists():
            self.remove_dislike(user)
        self.liked_by.add(user)

    def dislike(self, user: "User"):
        if self.liked_by.filter(id=user.id).exists():
            self.remove_like(user)
        self.disliked_by.add(user)

    def remove_like(self, user: "User"):
        self.liked_by.remove(user)

    def remove_dislike(self, user: "User"):
        self.disliked_by.remove(user)


class User(_Visible_Reportable_Model, AbstractUser):  # TODO: validate password at form level (https://docs.djangoproject.com/en/4.1/topics/auth/passwords/#module-django.contrib.auth.password_validation), prevent new accounts with similar usernames (especially verified accounts)
    first_name = None  # make blank in save method
    last_name = None
    get_full_name = None
    get_short_name = None

    username = models.CharField(
        _("username"),
        max_length=30,
        unique=True,
        help_text=_(
            "Required. 30 characters or fewer. Letters, digits and ./_ only."
        ),
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
            validate_tld_email
        ],
        error_messages={
            "unique": _(f"That Email Address is already in use by another user."),
        },
    )
    bio = models.TextField(
        "Bio",
        max_length=200,
        blank=True,
        null=True
    )
    verified = models.BooleanField("Verified", default=False)  # TODO: Add verification process
    following = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="followers",
        blank=True
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
        if self.email.count("@") == 1:
            local: str
            domain: str
            local, domain = self.email.split("@", maxsplit=1)

            local = local.replace(".", "")

            if "+" in local:
                local = local.split("+", maxsplit=1)[0]

            if domain == "googlemail.com":
                domain = "gmail.com"

            self.email = local + "@" + domain

        if EmailAddress.objects.filter(email=self.email).exclude(user=self).exists():
            raise ValidationError({"email": f"The Email Address: {self.email} is already in use by another user."}, code="unique")

        super().clean()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not EmailAddress.objects.filter(email=self.email, user=self).exists():
            current_primary_email_QS = EmailAddress.objects.filter(user=self, primary=True)
            if current_primary_email_QS.exists():
                old_primary = current_primary_email_QS.get()
                old_primary.primary = False
                old_primary.save()

            EmailAddress.objects.create(email=self.email, user=self, primary=True)


class Pulse(_User_Generated_Content_Model):  # TODO: disable the like & dislike buttons if profile already in set
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Creator",
        related_name="pulses"
    )  # NOTE: Provides a link to the Profile that created this Pulse
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_pulses",
        blank=True
    )
    disliked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="disliked_pulses",
        blank=True
    )

    @property
    def full_depth_replies(self):
        return Reply.objects.filter(_original_pulse=self)

    class Meta:
        verbose_name = "Pulse"

    def __str__(self):
        return f"{self.creator}, {self.string_when_visible(self.message[:settings.MESSAGE_DISPLAY_LENGTH])}"

    def save(self, *args, **kwargs):
        self.full_clean()

        if Pulse.objects.filter(id=self.id).exists():
            if not self.visible and Pulse.objects.get(id=self.id).visible:
                for reply in self.full_depth_replies:
                    reply.update(base_save=True, visible=False)

            elif self.visible and not Pulse.objects.get(id=self.id).visible:
                for reply in self.full_depth_replies:
                    reply.update(base_save=True, visible=True)

        super().save(*args, **kwargs)


class Reply(_User_Generated_Content_Model):  # TODO: disable the like & dislike buttons if profile already in set
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Creator",
        related_name="replies"
    )  # NOTE: Provides a link to the Profile that created this Reply
    _content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    _object_id = models.PositiveIntegerField()
    parent_object = GenericForeignKey(ct_field="_content_type", fk_field="_object_id")
    _original_pulse = models.ForeignKey(
        Pulse,
        on_delete=models.CASCADE,
        blank=True,
        verbose_name="Original Pulse",
        related_name="+"
    )
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_replies",
        blank=True
    )
    disliked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="disliked_replies",
        blank=True
    )

    @property
    def original_pulse(self):
        try:
            return self._original_pulse
        except Pulse.DoesNotExist:
            return self._find_original_pulse(self)

    class Meta:
        verbose_name = "Reply"
        verbose_name_plural = "Replies"

    def __str__(self):
        return f"{self.creator}, {self.string_when_visible(self.message[:settings.MESSAGE_DISPLAY_LENGTH])} (For object - {self.parent_object})"

    def save(self, *args, **kwargs):
        self._original_pulse = self.original_pulse

        if not self.original_pulse.visible:
            self.visible = False

        self.full_clean()
        self.base_save(clean=False, *args, **kwargs)

    @staticmethod
    def _find_original_pulse(reply):
        if isinstance(reply.parent_object, Pulse):
            return reply.parent_object
        return Reply._find_original_pulse(reply.parent_object)


class Report(Custom_Base_Model):  # TODO: create user privileges that can access reporting screens
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

    _content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    _object_id = models.PositiveIntegerField()
    parent_object = GenericForeignKey(ct_field="_content_type", fk_field="_object_id")
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Reporter",
        related_name="reports"
    )
    assigned_staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Assigned Staff Member",
        related_name="assigned_reports",
        limit_choices_to={"is_staff": True},
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
        verbose_name = "Reply"

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
        return f"{self.reporter}, {self.get_category_display()}, {self.get_status_display()} (Assigned Staff Member - {self.assigned_staff})(For object - {self.parent_object})"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
