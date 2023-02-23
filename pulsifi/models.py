"""
    Models in pulsifi app.
"""
import logging
import operator
from abc import abstractmethod
from functools import reduce
from typing import Final, Iterable

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, Group
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Manager, Q, QuerySet
from django.urls import reverse
from django.utils import timezone
from thefuzz.fuzz import token_sort_ratio as get_string_similarity
from tldextract import tldextract
from tldextract.tldextract import ExtractResult

from .models_utils import Custom_Base_Model, Date_Time_Created_Base_Model, get_random_moderator_id
from .validators import ConfusableEmailValidator, ConfusableStringValidator, ExampleEmailValidator, FreeEmailValidator, HTML5EmailValidator, PreexistingEmailTLDValidator, ReservedNameValidator


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
        verbose_name="Reports About This Object",
        help_text="Provides a link to the set of all :model:`pulsifi.report` objects that are reporting this object."
    )
    """
        Provides a link to the set of all :model:`pulsifi.report` objects that
        are reporting this object.
    """

    class Meta:
        abstract = True

    @property
    @abstractmethod
    def visible(self) -> bool:
        """
            Boolean flag to determine whether this object should be accessible
            to the website. Use this flag instead of deleting objects.
        """

        raise NotImplementedError

    @visible.setter
    @abstractmethod
    def visible(self, value: bool) -> None:
        raise NotImplementedError

    def delete(self, using: str = None, *args, **kwargs) -> tuple[int, dict[str, int]]:
        """
            Sets this instances visible field to False instead of deleting this
            instance's data from the database.
        """

        self.visible = False
        self.save()

        return 0, {}

    @abstractmethod
    def get_absolute_url(self):
        """ Returns the canonical URL for this object instance. """

        raise NotImplementedError

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
        Base model that defines fields for all types of user generated content,
        as well as extra instance methods for retrieving commonly computed
        properties.

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
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_%(class)s_set",
        blank=True,
        help_text="The set of :model:`pulsifi.user` instances that have liked this content object instance."
    )
    """
        The set of :model:`pulsifi.user` instances that have liked this content
        object instance.
    """

    disliked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="disliked_%(class)s_set",
        blank=True,
        help_text="The set of :model:`pulsifi.user` instances that have disliked this content object instance."
    )
    """
        The set of :model:`pulsifi.user` instances that have disliked this
        content object instance.
    """

    reply_set = GenericRelation(  # TODO: ratelimit whether user can create a new reply based on time between now and time of creation of last reply for same original_pulse
        "Reply",
        content_type_field="_content_type",
        object_id_field="_object_id",
        verbose_name="Replies",
        help_text="The set of :model:`pulsifi.reply` objects for this content object instance."
    )
    """
        The set of :model:`pulsifi.reply` objects for this content object
        instance.
    """

    visible = models.BooleanField(
        "Is visible?",
        default=True,
        help_text="Boolean flag to determine whether this object should be accessible to the website. Use this flag instead of deleting objects."
    )
    """
        Boolean flag to determine whether this object should be accessible
        to the website. Use this flag instead of deleting objects.
    """

    @property
    @abstractmethod
    def original_pulse(self) -> "Pulse":
        """
            The single :model:`pulsifi.pulse` object instance that is the
            highest parent object in the tree of :model:`pulsifi.pulse` &
            :model:`pulsifi.reply` objects that this instance is within.
        """

        raise NotImplementedError

    @property
    @abstractmethod
    def full_depth_replies(self) -> set["Reply"]:
        """
            The set of all :model:`pulsifi.reply` objects that are within the
            tree of this instance's children/children's children etc.
        """

        raise NotImplementedError

    class Meta:
        abstract = True

    def __str__(self) -> str:
        """
            Returns the stingified version of this content's creator and the
            message within this content if it is still visible, otherwise
            returns the crossed out message within this content.
        """

        return f"{self.creator}, {self.string_when_visible(self.message[:settings.MESSAGE_DISPLAY_LENGTH])}"

    def get_absolute_url(self) -> str:
        """ Returns the canonical URL for this object instance. """

        return f"""{reverse("pulsifi:feed")}?{type(self).__name__.lower()}={self.id}"""


class User(_Visible_Reportable_Model, AbstractUser):
    """
        Model to define changes to existing fields/extra fields & processing
        for users, beyond that/those given by Django's base :model:`auth.user`
        model.
    """

    STAFF_GROUP_NAMES = ["Moderators", "Admins"]

    first_name = None  # make blank in save method
    last_name = None
    get_full_name = None
    get_short_name = None

    moderator_assigned_report_set: Manager
    """
        The set of :model:`pulsifi.report` objects that this user (if they are
        a moderator) has been assigned to moderate.
    """

    avatar_set: Manager
    """
        The set of :model:`avatar.avatar` image objects that this user has
        uploaded.
    """

    disliked_pulse_set: Manager
    """ The set of :model:`pulsifi.pulse` objects that this user has disliked. """

    disliked_reply_set: Manager
    """ The set of :model:`pulsifi.reply` objects that this user has disliked. """

    # noinspection SpellCheckingInspection
    emailaddress_set: Manager
    # noinspection SpellCheckingInspection
    """
        The set of :model:`account.emailaddress` objects that have been
        assigned to this user.
    """

    liked_pulse_set: Manager
    """ The set of :model:`pulsifi.pulse` objects that this user has liked. """

    liked_reply_set: Manager
    """ The set of :model:`pulsifi.reply` objects that this user has liked. """

    created_pulse_set: Manager
    """ The set of :model:`pulsifi.pulse` objects that this user has created. """

    created_reply_set: Manager
    """ The set of :model:`pulsifi.reply` objects that this user has created. """

    submitted_report_set: Manager
    """
        The set of :model:`pulsifi.report` objects that this user has
        submitted.
    """
    # noinspection SpellCheckingInspection
    socialaccount_set: Manager
    """
        The set of :model:`socialaccount:socialaccount` objects that can be
        used to log in this user.
    """

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
        blank=True,
        help_text="Longer textfield containing an autobiographical description of this user."
    )
    """
        Longer textfield containing an autobiographical description of this
        user.
    """

    verified = models.BooleanField(  # TODO: Add verification process
        "Is verified?",
        default=False,
        help_text="Boolean flag to indicate whether this user is a noteable person/organisation."
    )
    """
        Boolean flag to indicate whether this user is a noteable
        person/organisation.
    """

    following = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="followers",
        blank=True,
        help_text="Set of other :model:`pulsifi.user` objects that this user is following."
    )
    """ Set of other :model:`pulsifi.user` objects that this user is following. """

    is_staff = models.BooleanField(
        "Is a staff member?",
        default=False,
        help_text="Boolean flag to indicate whether this user is a staff member, and thus can log into the admin site."
    )
    """
        Boolean flag to indicate whether this user is a staff member, and thus
        can log into the admin site.
    """

    is_superuser = models.BooleanField(
        "Is a superuser?",
        default=False,
        help_text="Boolean flag to provide a quick way to designate that this user has all permissions without explicitly assigning them."
    )
    """
        Boolean flag to provide a quick way to designate that this user has all
        permissions without explicitly assigning them.
    """

    is_active = models.BooleanField(
        "Is visible?",
        default=True,
        help_text="Boolean flag to determine whether this object should be accessible to the website. Use this flag instead of deleting objects."
    )
    """
        Boolean flag to determine whether this object should be accessible
        to the website. Use this flag instead of deleting objects.
    """

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
    def visible(self) -> bool:
        """
            Shortcut variable for the is_active property, to provide a
            consistent way to access the visibility of all objects in pulsifi
            app.
        """

        return self.is_active

    @visible.setter
    def visible(self, value: bool):
        self.is_active = value

    class Meta:
        verbose_name = "User"

    def __str__(self) -> str:
        """
            Returns this user's username, if they are still visible; otherwise
            returns the crossed out username.
        """

        return self.string_when_visible(f"@{self.username}")

    def clean(self) -> None:
        """
            Performs extra model-wide validation after clean() has been called
            on every field by self.clean_fields().
        """

        if self.is_superuser:  # NOTE: is_staff should be True if is_superuser is True
            self.is_staff = self.is_superuser

        query_restricted_admin_usernames = (Q(username__icontains=username) for username in settings.RESTRICTED_ADMIN_USERNAMES)
        restricted_admin_users_count: int = get_user_model().objects.exclude(id=self.id).filter(
            reduce(
                operator.or_,
                query_restricted_admin_usernames
            )
        ).count()
        restricted_admin_username_in_username = any(restricted_admin_username in self.username.lower() for restricted_admin_username in settings.RESTRICTED_ADMIN_USERNAMES)
        if (restricted_admin_users_count >= settings.PULSIFI_ADMIN_COUNT or not self.is_staff) and restricted_admin_username_in_username:  # NOTE: The username can only contain a restricted_admin_username if the user is a staff member & the maximum admin count has not been reached
            raise ValidationError({"username": "That username is not allowed."}, code="invalid")

        if get_user_model().objects.filter(id=self.id).exists():  # NOTE: Get all of the usernames except for this user
            username_check_list: Iterable[str] = get_user_model().objects.exclude(id=self.id).values_list("username", flat=True)
        else:
            username_check_list: Iterable[str] = get_user_model().objects.values_list("username", flat=True)

        for username in username_check_list:  # NOTE: Check this username is not too similar to any other username
            if get_string_similarity(self.username, username) >= settings.USERNAME_SIMILARITY_PERCENTAGE:
                raise ValidationError({"username": "That username is too similar to a username belonging to an existing user."}, code="unique")

        if self.email.count("@") == 1:
            local: str
            whole_domain: str
            local, whole_domain = self.email.split("@", maxsplit=1)

            extracted_domain = tldextract.extract(whole_domain)

            local = local.replace(".", "")  # NOTE: Format the local part of the email address to remove dots

            if "+" in local:
                local = local.split("+", maxsplit=1)[0]  # NOTE: Format the local part of the email address to remove any part after a plus symbol

            if extracted_domain.domain == "googlemail":  # NOTE: Rename alias email domains (E.g. googlemail == gmail)
                # noinspection PyArgumentList
                extracted_domain = ExtractResult(subdomain=extracted_domain.subdomain, domain="gmail", suffix=extracted_domain.suffix)

            else:
                query_restricted_admin_usernames = (Q(username__icontains=username) for username in settings.RESTRICTED_ADMIN_USERNAMES)
                restricted_admin_users_count: int = get_user_model().objects.exclude(id=self.id).filter(
                    reduce(
                        operator.or_,
                        query_restricted_admin_usernames
                    )
                ).count()
                restricted_admin_username_in_username = any(restricted_admin_username in extracted_domain.domain for restricted_admin_username in settings.RESTRICTED_ADMIN_USERNAMES)
                if (restricted_admin_users_count >= settings.PULSIFI_ADMIN_COUNT or not self.is_staff) and restricted_admin_username_in_username:  # NOTE: The email domain can only contain a restricted_admin_username if the user is a staff member & the maximum admin count has not been reached
                    raise ValidationError({"email": f"That Email Address cannot be used."}, code="invalid")

            self.email = "@".join([local, extracted_domain.fqdn])  # NOTE: Replace the cleaned email address

        if EmailAddress.objects.filter(email=self.email).exclude(user=self).exists():
            raise ValidationError({"email": f"The Email Address: {self.email} is already in use by another user."}, code="unique")

        if self.verified:
            NO_EMAIL_ERROR = ValidationError({"verified": "User cannot become verified without at least one verified email address."})
            if get_user_model().objects.filter(id=self.id).exists():
                if not self.emailaddress_set.filter(verified=True).exists():
                    raise NO_EMAIL_ERROR
            else:  # NOTE: User cannot be verified upon initial creation because no verified EmailAddress objects will exist yet
                raise NO_EMAIL_ERROR

        super().clean()

    def save(self, *args, **kwargs) -> None:
        # noinspection SpellCheckingInspection
        """
            Saves the current instance to the database then performs extra
            cleanup of relations (E.g. removing self from followers or ensuring
            an :model:`account.emailaddress` object exists for the user's
            primary email).
        """

        self_already_exists: bool = get_user_model().objects.filter(id=self.id).exists()

        super().save(*args, **kwargs)

        self.ensure_superuser_in_admin_group()
        self.ensure_user_in_any_staff_group_is_staff()

        if self in self.following.all():
            self.following.remove(self)

        if self in self.followers.all():
            self.followers.remove(self)

        if self_already_exists and not EmailAddress.objects.filter(email=self.email, user=self).exists():  # HACK: Checking for EmailAddress object existence (for primary email) cannot be done upon creation because EmailAddress objects are created after user save during signup flow
            try:
                old_primary_email = EmailAddress.objects.get(user=self, primary=True)  # NOTE: Make existing EmailAddress object marked as primary not primary
            except EmailAddress.DoesNotExist:
                pass
            else:
                old_primary_email.primary = False
                old_primary_email.save()

            EmailAddress.objects.create(email=self.email, user=self, primary=True)

    def ensure_user_in_any_staff_group_is_staff(self) -> None:
        """
            Ensures that if the current user instance has been added to any of
            the staff :model:`auth.group` objects, then they should have the
            is_staff property set to True.
        """

        index = 0
        while not self.is_staff and index < len(self.STAFF_GROUP_NAMES):
            try:
                if Group.objects.get(name=self.STAFF_GROUP_NAMES[index]) in self.groups.all():
                    self.update(is_staff=True)
            except Group.DoesNotExist:
                logging.error(f"Could not check whether User: {self} is in \"{self.STAFF_GROUP_NAMES[index]}\" group because it does not exist.")
            finally:
                index += 1

    def ensure_superuser_in_admin_group(self) -> None:
        """
            Ensures that if the current user instance has the is_superuser
            property set to True then they should be added to the Admins
            :model:`auth.group`.
        """

        if self.is_superuser:
            try:
                admin_group = Group.objects.get(name="Admins")
            except Group.DoesNotExist:
                logging.error(f"User: {self} is superuser but could not be added to \"Admins\" group because it does not exist.")
            else:
                if admin_group not in self.groups.all():
                    self.groups.add(admin_group)

    def get_absolute_url(self) -> str:
        """ Returns the canonical URL for this object instance. """

        return reverse("pulsifi:specific_account", kwargs={"username": self.username})

    def get_feed_pulses(self) -> QuerySet["Pulse"]:
        """
            Returns the set of :model:`pulsifi.pulse` objects that should be
            displayed on the :view:`pulsifi.views.Feed_View` for this user.
        """  # BUG: Admindocs does not generate link to view correctly

        return Pulse.objects.filter(
            creator__in=self.following.exclude(is_active=False)
        ).order_by("_date_time_created")

    @classmethod
    def get_proxy_field_names(cls) -> set[str]:
        """
            Returns a set of names of extra properties of this model that can
            be saved to the database, even though those fields don't actually
            exist. They are just proxy fields.
        """

        extra_property_fields: set[str] = super().get_proxy_field_names()

        extra_property_fields.add("visible")

        return extra_property_fields


class Pulse(_User_Generated_Content_Model):  # TODO: disable the like & dislike buttons if profile already in set
    """
        Model to define pulses (posts) that are made by users and are visible
        on the main website.
    """

    class Meta:
        verbose_name = "Pulse"

    def save(self, *args, **kwargs) -> None:
        """
            Saves the current instance to the database, after making any
            :model:`pulsifi.reply` objects, of this instance, the matching
            visibility, to this pulse's visibility.
        """

        self.full_clean()

        try:
            old_visible = Pulse.objects.get(id=self.id).visible
        except Pulse.DoesNotExist:
            pass
        else:
            if not self.visible and old_visible:
                for reply in self.full_depth_replies:
                    reply.update(base_save=True, visible=False)

            elif self.visible and not old_visible:
                for reply in self.full_depth_replies:
                    reply.update(base_save=True, visible=True)

        super().save(*args, **kwargs)

    @property
    def original_pulse(self) -> "Pulse":
        """
            Returns the :model:`pulsifi.pulse` object that is the highest
            parent object in the tree of :model:`pulsifi.pulse` &
            :model:`pulsifi.reply` objects that this instance is within.

            The highest User_Generated_Content object within the current
            replies-tree is always a :model:`pulsifi.pulse` object.
        """

        return self

    @property
    def full_depth_replies(self) -> set["Reply"]:
        """
            The set of all :model:`pulsifi.reply` objects that are within the
            tree of this instance's children/children's children etc.
        """

        return {reply for reply in Reply.objects.all() if reply.original_pulse is self}


class Reply(_User_Generated_Content_Model):  # TODO: disable the like & dislike buttons if profile already in set
    """
        Model to define replies (posts assigned to a parent
        :model:`pulsifi.pulse` object) that are made by a :model:`pulsifi.user`
        and visible on the main website (underneath the corresponding
        :model:`pulsifi.pulse`).
    """

    _content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={"app_label": "pulsifi", "model__in": ("pulse", "reply")},
        verbose_name="Replied Content Type",
        help_text="Link to the content type of the replied_content instance (either :model:`pulsifi.pulse` or :model:`pulsifi.reply`)."
    )
    """
        Link to the content type of the replied_content instance (either
        :model:`pulsifi.pulse` or :model:`pulsifi.reply`).
    """

    _object_id = models.PositiveIntegerField(
        verbose_name="Replied Content ID",
        help_text="ID number of the specific instance of the replied_content instance."
    )
    """ ID number of the specific instance of the replied_content instance. """

    replied_content = GenericForeignKey(ct_field="_content_type", fk_field="_object_id")
    """
        Shortcut variable for the instance of replied_content, determined from
        the _content_type and _object_id.
    """

    @property
    def original_pulse(self) -> Pulse:
        """
            The single :model:`pulsifi.pulse` object instance that is the
            highest parent object in the tree of :model:`pulsifi.pulse` &
            :model:`pulsifi.reply` objects that this instance is within.
        """

        return self.replied_content.original_pulse

    @property
    def full_depth_replies(self) -> set["Reply"]:
        """
            The set of all :model:`pulsifi.reply` objects that are within the
            tree of this instance's children/children's children etc.
        """

        replies = set()
        reply: "Reply"
        for reply in self.reply_set.all():
            replies.add(reply)  # NOTE: Add the current level :model:`pulsifi.reply` objects to the set
            replies.update(reply.full_depth_replies)  # NOTE: Add the child :model:`pulsifi.reply` objects recursively to the set
        return replies

    class Meta:
        verbose_name = "Reply"
        verbose_name_plural = "Replies"
        indexes = [
            models.Index(fields=["_content_type", "_object_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.creator}, {self.string_when_visible(self.message[:settings.MESSAGE_DISPLAY_LENGTH])} (For object - {type(self.replied_content).__name__.upper()[0]} | {self.replied_content})"[:100]

    def clean(self) -> None:
        """
            Performs extra model-wide validation after clean() has been called
            on every field by self.clean_fields().
        """

        try:
            if self._content_type not in ContentType.objects.filter(app_label="pulsifi", model__in=("pulse", "reply")):  # BUG: causes error when making reply to a pulse
                raise ValidationError({"_content_type": f"The Content Type: {self._content_type} is not one of the allowed options: Pulse, Reply."}, code="invalid")

            if self._content_type == ContentType.objects.get(app_label="pulsifi", model="reply") and self._object_id == self.id:
                raise ValidationError({"_object_id": "Replied content cannot be this Reply."}, code="invalid")

            if (self._content_type == ContentType.objects.get(app_label="pulsifi", model="pulse") and self._object_id not in Pulse.objects.all().values_list("id", flat=True)) or (self._content_type == ContentType.objects.get(app_label="pulsifi", model="reply") and self._object_id not in Reply.objects.all().values_list("id", flat=True)):
                raise ValidationError("Replied content must be valid object.")

        except ContentType.DoesNotExist as e:
            e.args = ("Replied object could not be correctly verified because content types for Pulses or Replies do not exist.",)
            raise e

        super().clean()

    def save(self, *args, **kwargs) -> None:
        """
            Saves the current instance to the database, after ensuring the
            current instance is not visible if the original_pulse is not
            visible.
        """

        self.full_clean()

        if not self.original_pulse.visible:
            self.visible = False

        self.base_save(clean=False, *args, **kwargs)


class Report(Custom_Base_Model, Date_Time_Created_Base_Model):
    """
        Model to define reports, which flags inappropriate content/users to
        moderators.
    """

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
    """ List of category code & display values of each category. """

    status_choices = [
        (IN_PROGRESS, "In Progress"),
        (REJECTED, "Rejected"),
        (COMPLETED, "Completed")
    ]
    """ List of status code & display values of each status. """

    _content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={"app_label": "pulsifi", "model__in": settings.REPORTABLE_CONTENT_TYPE_NAMES},
        verbose_name="Reported Object Type",
        help_text="Link to the content type of the reported_object instance (either :model:`pulsifi.user`, :model:`pulsifi.pulse` or :model:`pulsifi.reply`)."
    )
    """
        Link to the content type of the reported_object instance (either
        :model:`pulsifi.user`, :model:`pulsifi.pulse` or
        :model:`pulsifi.reply`).
    """

    _object_id = models.PositiveIntegerField(
        verbose_name="Reported Object ID",
        help_text="ID number of the specific instance of the reported_object instance."
    )
    """ ID number of the specific instance of the reported_object instance. """

    reported_object = GenericForeignKey(ct_field="_content_type", fk_field="_object_id")
    """
        Shortcut variable for the instance of reported_object, determined from
        the _content_type and _object_id.
    """

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Reporter",
        related_name="submitted_report_set",
        help_text="Link to the :model:`pulsifi.user` object instance that created this report."
    )
    """
        Link to the :model:`pulsifi.user` object instance that created this
        report.
    """

    assigned_moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Assigned Moderator",
        related_name="moderator_assigned_report_set",
        limit_choices_to={"groups__name": "Moderators", "is_active": True},
        default=get_random_moderator_id,
        help_text="Link to the :model:`pulsifi.user` object instance (from the set of moderators) that has been assigned to moderate this report."
    )
    """
        Link to the :model:`pulsifi.user` object instance (from the set of
        moderators) that has been assigned to moderate this report.
    """

    reason = models.TextField(
        "Reason",
        help_text="Longer textfield containing an detailed description of the reason for this report's existence."
    )
    """
        Longer textfield containing an detailed description of the reason for
        this report's existence.
    """

    category = models.CharField(
        "Category",
        max_length=3,
        choices=category_choices,
        help_text="The category code that gives an overview as to the reason for the report."
    )
    """
        The category code that gives an overview as to the reason for the
        report.
    """

    status = models.CharField(
        "Status",
        max_length=2,
        choices=status_choices,
        default=IN_PROGRESS,
        help_text="The status code that outlines the current position within the moderation cycle that this report is within."
    )
    """
        The status code that outlines the current position within the
        moderation cycle that this report is within.
    """

    class Meta:
        verbose_name = "Report"
        indexes = [
            models.Index(fields=["_content_type", "_object_id"]),
        ]

    # noinspection PyFinal
    def __init__(self, *args, **kwargs) -> None:  # HACK: Make instance constants final by using type hinting & reassigning the original values from the class constants
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

    def __str__(self) -> str:
        return f"{self.reporter}, {self.category}, {self.get_status_display()} (For object - {type(self.reported_object).__name__.upper()[0]} | {self.reported_object})(Assigned Moderator - {self.assigned_moderator})"

    def clean(self) -> None:
        """
            Performs extra model-wide validation after clean() has been called
            on every field by self.clean_fields().
        """

        try:
            if self._content_type not in ContentType.objects.filter(app_label="pulsifi", model__in=settings.REPORTABLE_CONTENT_TYPE_NAMES):
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

                if self.assigned_moderator_id == self._object_id:  # NOTE: Attempt to pick a different moderator if the default is the reported user
                    try:
                        self.assigned_moderator_id = get_random_moderator_id([self._object_id])
                    except get_user_model().DoesNotExist as e:
                        raise ValidationError({"_object_id": "This object ID refers to the only moderator available to be assigned to this report. Therefore, this moderator cannot be reported."}, code="invalid") from e

        except ContentType.DoesNotExist as e:
            e.args = ("Reported object could not be correctly verified because content types for Pulses, Replies or Users do not exist.",)
            raise e

        if self.assigned_moderator == self.reporter:  # NOTE: Attempt to pick a different moderator if the default is the reporter
            try:
                # noinspection PyTypeChecker
                self.assigned_moderator_id = get_random_moderator_id([self.reporter_id])
            except get_user_model().DoesNotExist as e:
                raise ValidationError({"reporter": "This user cannot be the reporter because they are the only moderator available to be assigned to this report"}, code="invalid") from e

        super().clean()
