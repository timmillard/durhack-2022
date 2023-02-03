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
from thefuzz.fuzz import token_sort_ratio as get_string_similarity
from tldextract import tldextract
from tldextract.tldextract import ExtractResult

from .models_utils import Custom_Base_Model, Date_Time_Created_Base_Model, get_random_staff_member_id
from .validators import ConfusableEmailValidator, ConfusableStringValidator, ExampleEmailValidator, FreeEmailValidator, HTML5EmailValidator, PreexistingEmailTLDValidator, ReservedNameValidator

logger = logging.getLogger(__name__)


class _Visible_Reportable_Model(Custom_Base_Model):
    """
        Base model that prevents objects from actually being deleted (making
        them invisible instead), as well as allowing all objects of this type
        to have reports made about them.

        This class is abstract so should not be instantiated or have a table
        made for it in the database (see
        https://docs.djangoproject.com/en/4.1/topics/db/models/#abstract-base-classes).
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

    class Meta:
        abstract = True

    @property
    @abstractmethod
    def visible(self) -> bool:
        """
            Abstract declaration of visible field getter that MUST be
            implemented by child classes.
        """

        raise NotImplementedError

    @visible.setter
    @abstractmethod
    def visible(self, value: bool) -> None:
        """
            Abstract declaration of visible field setter that MUST be
            implemented by child classes.
        """

        raise NotImplementedError

    def delete(self, using: str = None, *args, **kwargs):
        self.visible = False
        self.save()

    def string_when_visible(self, string: str):
        """
            Returns the given string, or the given string but crossed out if
            this object is not visible.

            (string gets crossed out by adding the unicode strikethrough
            character between every character in the string).
        """

        if self.visible:
            return string
        return "".join(f"{char}\u0336" for char in string)


class _User_Generated_Content_Model(_Visible_Reportable_Model, Date_Time_Created_Base_Model):  # TODO: calculate time remaining based on engagement (decide {just likes}, {likes & {likes of replies}} or {likes, {likes of replies} & replies}) & creator follower count
    """


        This class is abstract so should not be instantiated or have a table
        made for it in the database (see
        https://docs.djangoproject.com/en/4.1/topics/db/models/#abstract-base-classes).
    """

    message = models.TextField("Message")
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Creator",
        related_name="created_%(class)s_set"
    )
    """
        Provides a link to the Profile that created this User_Generated_Content.
    """

    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_%(class)s_set",
        blank=True
    )
    disliked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="disliked_%(class)s_set",
        blank=True
    )
    reply_set = GenericRelation(  # TODO: ratelimit whether user can create a new reply based on time between now and time of creation of last reply for same original_pulse
        "Reply",
        content_type_field="_content_type",
        object_id_field="_object_id",
        verbose_name="Replies"
    )
    visible = models.BooleanField("Is visible?", default=True)

    @property
    @abstractmethod
    def original_pulse(self) -> "Pulse":
        """
            Abstract declaration of original_pulse field getter that MUST be
            implemented by child classes.
        """

        raise NotImplementedError

    @property
    @abstractmethod
    def full_depth_replies(self) -> list["Reply"]:
        """
            Abstract declaration of full_depth_replies field getter that MUST
            be implemented by child classes.
        """

        raise NotImplementedError

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.creator}, {self.string_when_visible(self.message[:settings.MESSAGE_DISPLAY_LENGTH])}"

    def get_absolute_url(self):
        return f"""{reverse("pulsifi:feed")}?{type(self).__name__.lower()}={self.id}"""


class User(_Visible_Reportable_Model, AbstractUser):
    STAFF_GROUP_NAMES = ["Moderators", "Admins"]

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
        "Username",
        max_length=30,
        unique=True,
        validators=[
            RegexValidator(
                r"^[\w.-]+\Z",
                "Enter a valid username. This value may contain only letters, digits and ./_ characters."
            ),
            ReservedNameValidator,
            ConfusableStringValidator
        ],
        error_messages={
            "unique": "A user with that username already exists."
        }
    )
    email = models.EmailField(
        "Email Address",
        unique=True,
        validators=[
            HTML5EmailValidator,
            FreeEmailValidator,
            ConfusableEmailValidator,
            PreexistingEmailTLDValidator,
            ExampleEmailValidator
        ],
        error_messages={
            "unique": f"That Email Address is already in use by another user."
        }
    )
    bio = models.TextField(
        "Bio",
        max_length=200,
        blank=True
    )
    verified = models.BooleanField("Is verified?", default=False)  # TODO: Add verification process
    following = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="followers",
        blank=True
    )
    is_staff = models.BooleanField(
        "Is a staff member?",
        default=False,
        help_text="Designates whether the user can log into this admin site."
    )
    is_superuser = models.BooleanField(
        "Is a superuser?",
        default=False,
        help_text="Designates that this user has all permissions without explicitly assigning them."
    )
    is_active = models.BooleanField(
        "Is visible?",
        default=True,
        help_text="Designates whether this user is visible. Unselect this instead of deleting accounts.",
    )
    date_joined = models.DateTimeField(
        "Date Joined",
        default=timezone.now,
        editable=False
    )
    last_login = models.DateTimeField(
        "Last Login",
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

    def __str__(self):
        """
            Returns the User's username if they are still visible, otherwise
            returns the crossed out username.
        """

        return self.string_when_visible(f"@{self.username}")

    def clean(self):
        if self.is_superuser:
            self.is_staff = self.is_superuser

        if (get_user_model().objects.filter(username__icontains="pulsifi").count() > settings.PULSIFI_ADMIN_COUNT or not self.is_staff) and "pulsifi" in self.username.lower():
            raise ValidationError({"username": "That username is not allowed."}, code="invalid")

        if get_user_model().objects.filter(id=self.id).exists():
            username_check_list: list[str] = get_user_model().objects.exclude(id=self.id).values_list("username", flat=True)
        else:
            username_check_list: list[str] = get_user_model().objects.values_list("username", flat=True)
        for username in username_check_list:
            if get_string_similarity(self.username, username) >= settings.USERNAME_SIMILARITY_PERCENTAGE:
                raise ValidationError({"username": "That username is too similar to a username belonging to an existing user."}, code="unique")

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
            NO_EMAIL_ERROR = ValidationError({"verified": "User cannot become verified without at least one verified email address."})
            if get_user_model().objects.filter(id=self.id).exists():
                if not self.emailaddress_set.filter(verified=True).exists():
                    raise NO_EMAIL_ERROR
            else:
                raise NO_EMAIL_ERROR

        super().clean()

    def save(self, *args, **kwargs):
        self_already_exists: bool = get_user_model().objects.filter(id=self.id).exists()

        super().save(*args, **kwargs)

        self.ensure_superuser_in_admin_group()
        self.ensure_user_in_moderator_or_admin_group_is_staff()

        if self in self.following.all():
            self.following.remove(self)

        if self_already_exists and not EmailAddress.objects.filter(email=self.email, user=self).exists():
            old_primary_email_QS = EmailAddress.objects.filter(user=self, primary=True)
            if old_primary_email_QS.exists():
                old_primary_email = old_primary_email_QS.get()
                old_primary_email.primary = False
                old_primary_email.save()

            EmailAddress.objects.create(email=self.email, user=self, primary=True)

    def ensure_user_in_moderator_or_admin_group_is_staff(self):
        index = 0
        while not self.is_staff and index < len(self.STAFF_GROUP_NAMES):
            group_QS = Group.objects.filter(name=self.STAFF_GROUP_NAMES[index])
            if group_QS.exists():
                group = group_QS.get()
                if group in self.groups.all():
                    self.update(is_staff=True)
            else:
                logger.error(f"""Could not check whether User: {self} is in "{self.STAFF_GROUP_NAMES[index]}" group because it does not exist.""")
            index += 1

    def ensure_superuser_in_admin_group(self):
        if self.is_superuser:
            admin_group_QS = Group.objects.filter(name="Admins")
            if admin_group_QS.exists():
                admin_group = admin_group_QS.get()
                if admin_group not in self.groups.all():
                    self.groups.add(admin_group)
            else:
                logger.error(f"""User: {self} is superuser but could not be added to "Admins" group because it does not exist.""")

    def get_absolute_url(self):
        return reverse("pulsifi:specific_account", kwargs={"username": self.username})


class Pulse(_User_Generated_Content_Model):  # TODO: disable the like & dislike buttons if profile already in set
    class Meta:
        verbose_name = "Pulse"

    def save(self, *args, **kwargs):
        self.full_clean()

        self_QS = Pulse.objects.filter(id=self.id)

        if self_QS.exists():
            old_visible = self_QS.get().visible
            if not self.visible and old_visible:
                for reply in self.full_depth_replies:
                    reply.update(base_save=True, visible=False)

            elif self.visible and not old_visible:
                for reply in self.full_depth_replies:
                    reply.update(base_save=True, visible=True)

        super().save(*args, **kwargs)

    @property
    def original_pulse(self):
        return self

    @property
    def full_depth_replies(self):
        return [reply for reply in Reply.objects.all() if reply.original_pulse is self]


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
        return self.replied_content.original_pulse

    @property
    def full_depth_replies(self):
        replies = []
        reply: "Reply"
        for reply in self.reply_set.all():
            replies.append(reply)
            replies.extend(reply.full_depth_replies)
        return replies

    class Meta:
        verbose_name = "Reply"
        verbose_name_plural = "Replies"
        indexes = [
            models.Index(fields=["_content_type", "_object_id"]),
        ]

    def __str__(self):
        return f"{self.creator}, {self.string_when_visible(self.message[:settings.MESSAGE_DISPLAY_LENGTH])} (For object - {type(self.replied_content).__name__.upper()[0]} | {self.replied_content})"[:100]

    def clean(self):
        try:
            if self._content_type not in ContentType.objects.filter(app_label="pulsifi", model__in=("pulse", "reply")):
                raise ValidationError({"_content_type": f"The Content Type: {self._content_type} is not one of the allowed options: Pulse, Reply."}, code="invalid")

            if self._content_type == ContentType.objects.get(app_label="pulsifi", model="reply") and self._object_id == self.id:
                raise ValidationError({"_object_id": "Replied content cannot be this Reply."}, code="invalid")

            if (self._content_type == ContentType.objects.get(app_label="pulsifi", model="pulse") and self._object_id not in Pulse.objects.all().values_list("id", flat=True)) or (self._content_type == ContentType.objects.get(app_label="pulsifi", model="reply") and self._object_id not in Reply.objects.all().values_list("id", flat=True)):
                raise ValidationError("Replied content must be valid object.")

        except ContentType.DoesNotExist as e:
            e.args = ("Replied object could not be correctly verified because content types for Pulses or Replies do not exist.",)
            raise e

        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()

        if not self.original_pulse.visible:
            self.visible = False

        self.base_save(clean=False, *args, **kwargs)


class Report(Custom_Base_Model, Date_Time_Created_Base_Model):
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
        limit_choices_to={"groups__name": "Moderators", "is_active": True},
        default=get_random_staff_member_id
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
        return f"{self.reporter}, {self.category}, {self.get_status_display()} (For object - {type(self.reported_object).__name__.upper()[0]} | {self.reported_object})(Assigned Staff Member - {self.assigned_staff_member})"

    def clean(self):
        try:
            if self._content_type not in ContentType.objects.filter(app_label="pulsifi", model__in=("user", "pulse", "reply")):
                raise ValidationError({"_content_type": f"The Content Type: {self._content_type} is not one of the allowed options: User, Pulse, Reply."}, code="invalid")

            elif (self._content_type == ContentType.objects.get(app_label="pulsifi", model="user") and self._object_id not in get_user_model().objects.all().values_list("id", flat=True)) or (self._content_type == ContentType.objects.get(app_label="pulsifi", model="pulse") and self._object_id not in Pulse.objects.all().values_list("id", flat=True)) or (self._content_type == ContentType.objects.get(app_label="pulsifi", model="reply") and self._object_id not in Reply.objects.all().values_list("id", flat=True)):
                raise ValidationError("Reported object must be valid object.")

            elif self._content_type == ContentType.objects.get(app_label="pulsifi", model="pulse") or self._content_type == ContentType.objects.get(app_label="pulsifi", model="reply"):
                REPORT_ADMIN_CONTENT_ERROR = ValidationError({"_object_id": "This object ID refers to a Pulse or Reply created by an Admin. These Pulses & Replies cannot be reported."}, code="invalid")
                if Group.objects.filter(name="Admins").exists():
                    if self.reported_object.creator in get_user_model().objects.filter(Q(groups__name="Admins") | Q(is_superuser=True)):
                        raise REPORT_ADMIN_CONTENT_ERROR
                elif self.reported_object.creator in get_user_model().objects.filter(is_superuser=True):
                    raise REPORT_ADMIN_CONTENT_ERROR

            elif self._content_type == ContentType.objects.get(app_label="pulsifi", model="user"):
                if self._object_id == self.reporter_id:
                    raise ValidationError({"_object_id": f"The reporter cannot create a report about themself."}, code="invalid")  # TODO: Better error message
                else:
                    REPORT_ADMIN_ERROR = ValidationError({"_object_id": "This object ID refers to an admin. Admins cannot be reported."}, code="invalid")
                    if Group.objects.filter(name="Admins").exists():
                        if self._object_id in get_user_model().objects.filter(Q(groups__name="Admins") | Q(is_superuser=True)).values_list("id", flat=True):
                            raise REPORT_ADMIN_ERROR
                    elif self._object_id in get_user_model().objects.filter(is_superuser=True).values_list("id", flat=True):
                        raise REPORT_ADMIN_ERROR

                if self.assigned_staff_member_id == self._object_id:
                    try:
                        self.assigned_staff_member_id = get_random_staff_member_id([self._object_id])
                    except get_user_model().DoesNotExist as e:
                        raise ValidationError({"_object_id": "This object ID refers to the only moderator available to be assigned to this report. Therefore, this moderator cannot be reported."}, code="invalid") from e

        except ContentType.DoesNotExist as e:
            e.args = ("Reported object could not be correctly verified because content types for Pulses, Replies or Users do not exist.",)
            raise e

        print(type([self.reporter_id]))
        if self.assigned_staff_member == self.reporter:
            try:
                # noinspection PyTypeChecker
                self.assigned_staff_member_id = get_random_staff_member_id([self.reporter_id])
            except get_user_model().DoesNotExist as e:
                raise ValidationError({"reporter": "This user cannot be the reporter because they are the only moderator available to be assigned to this report"}, code="invalid") from e

        super().clean()
