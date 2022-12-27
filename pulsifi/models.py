"""
    Models in pulsifi application.
"""
from abc import abstractmethod
from datetime import datetime
from random import choice as random_choice
from typing import Iterable

import unicodedata
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth.models import User as BaseUser, UserManager
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.options import Options


def _choose_default_assigned_staff():
    """
        Returns a random staff member's Profile to be used as the default for a
        newly created report.
    """

    staff_QS = Profile.objects.filter(_base_user__is_staff=True)

    if staff_QS.exists():
        return Profile.objects.filter(
            id=random_choice(staff_QS.values_list("id", flat=True))
        ).get().id  # Choose a random ID from the list of staff member IDs

    return None  # Set the link to a staff member's ID to None because no staff members currently xist in the database (will cause a validation error on Report because assigned_staff cannot be null, so staff members should be added before reports are made)


class _Custom_Base_Model(models.Model):
    """
        Base model that provides extra utility methods for all other models to
        use.
    """

    class Meta:  # This class is abstract (only used for inheritance) so should not be able to be instantiated or have a table made for it in the database
        abstract = True

    def base_save(self, clean=True, *args, **kwargs):
        if clean:
            self.full_clean()
        models.Model.save(self, *args, **kwargs)

    def refresh_from_db(self, using: str = None, fields: Iterable[str] = None, deep=True):
        """
            Custom implementation of refreshing in-memory objects from the
            database, which also updates any related fields on this object.
        """

        super().refresh_from_db(using=using, fields=fields)  # Update all normal fields using the base refresh_from_db method

        if deep:
            if fields:
                update_fields = [field for field in self._meta.get_fields(include_hidden=True) if field in fields and field.name != "+"]  # Limit the fields to be updated by the ones supplied in the "fields" argument with a valid field name (not a "+")
            else:
                update_fields = [field for field in self._meta.get_fields() if field.name != "+"]  # Limit the fields to be updated by the ones with a valid field name (not a "+")

            updated_model = self._meta.model.objects.get(id=self.id)  # Get the updated version of the object from the database (for related fields to be replaced from)

            field: models.Field
            for field in update_fields:
                if field.is_relation and not isinstance(field, models.ManyToManyField) and not isinstance(field, GenericRelation):  # Limit the fields to be updated by the ones that are not a queryset of related objects
                    try:
                        setattr(self, field.name, getattr(updated_model, field.name))  # Set the value of the field to be that of the corresponding field retrieved from the database
                    except (AttributeError, TypeError, ValueError) as e:
                        pass  # TODO: use logging to log the error

    def update(self, commit=True, base_save=False, clean=True, **kwargs):
        """
            Changes an in-memory object's values & save that object to the
            database all in one operation (based on Django's
            Queryset.bulk_update method).
        """

        for key, value in kwargs.items():  # Update the values of the kwargs provided
            setattr(self, key, value)

        if commit:  # Save the new object's state to the database as long as commit has been requested
            if base_save:  # Use the base_save method of the model to save the object (if specified), only cleaning the object if specified
                self.base_save(clean)
            else:
                self.save()  # Otherwise use the normal full save method of the model to save the object


class _Visible_Reportable_Model(_Custom_Base_Model):
    """
        Base model that prevents objects from actually being deleted (making
        them invisible instead), as well as allowing all objects of this type
        to have reports made about them.
    """

    reports = GenericRelation(
        "Report",
        content_type_field='_content_type',
        object_id_field='_object_id',
        related_query_name="reverse_parent_object",
        verbose_name="Reports"
    )
    """
        Provides a link to the set of all Report objects that link to this
        object.
    """

    class Meta:  # This class is abstract (only used for inheritance) so should not be able to be instantiated or have a table made for it in the database
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

    def string_when_visible(self, string: str):
        """
            Returns the given string, or the given string but crossed out if
            this object is not visible.
        """

        if self.visible:
            return string
        return "".join(f"{char}\u0336" for char in string)  # Adds the unicode strikethrough character between every character in the given string, to "cross out" the given string


class _User_Generated_Content_Model(_Visible_Reportable_Model):  # TODO: calculate time remaining based on engagement & creator follower count
    visible = models.BooleanField("Visibility", default=True)
    message = models.TextField("Message")
    replies = GenericRelation(
        "Reply",
        content_type_field='_content_type',
        object_id_field='_object_id',
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

    class Meta:  # This class is abstract (only used for inheritance) so should not be able to be instantiated or have a table made for it in the database
        abstract = True

    def __str__(self):
        return self.string_when_visible(self.message[:settings.MESSAGE_DISPLAY_LENGTH])

    def delete(self, *args, **kwargs):  # TODO: prevent deletion (just set visibility to false)
        return super().delete(*args, **kwargs)

    def like(self, profile: "Profile"):  # TODO: prevent users from increasing the time by liking then unliking then reliking
        if self.disliked_by.filter(id=profile.id).exists():
            self.remove_dislike(profile)
        self.liked_by.add(profile)

    def dislike(self, profile: "Profile"):
        if self.liked_by.filter(id=profile.id).exists():
            self.remove_like(profile)
        self.disliked_by.add(profile)

    def remove_like(self, profile: "Profile"):
        self.liked_by.remove(profile)

    def remove_dislike(self, profile: "Profile"):
        self.disliked_by.remove(profile)


class Profile(_Visible_Reportable_Model):  # TODO: limit characters allowed in username & password, prevent new accounts with similar usernames (especially verified accounts)
    """
        Custom expansion class that holds extra data about a user (specific to
        Pulsifi).
    """

    _base_user = models.OneToOneField(
        BaseUser, null=True, on_delete=models.SET_NULL
    )  # Field is set to null if the underlying User object is deleted, so that as much information & functionality is retained
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
    )  # Provides a link to the set of other Profiles that this object is following (as well as an implied reverse set of followers)

    @property
    def base_user(self):  # Public getter for the private field _base_user
        if self._base_user is not None:
            return self._base_user
        return self._Null_BaseUser(profile=self)

    @property
    def username(self) -> str:  # Shortcut getter for the field base_user.username
        # noinspection PyTypeChecker
        return self.base_user.username

    @property
    def email(self) -> str:  # Shortcut getter for the field base_user.email
        # noinspection PyTypeChecker
        return self.base_user.email

    @property
    def date_joined(self) -> datetime:
        # noinspection PyTypeChecker
        return self.base_user.date_joined

    @property
    def visible(self):
        return self.base_user.is_active

    # noinspection SpellCheckingInspection
    @property
    def emailaddress_set(self) -> models.Manager:
        # noinspection PyTypeChecker
        return self.base_user.emailaddress_set

    class Meta:
        verbose_name = "User"

    # Large class definition coming up, with lots of boilerplate (it may be helpful to collapse this class in your IDE)
    class _Null_BaseUser:
        # noinspection PyPropertyDefinition
        @property
        def username(self):
            self._does_not_exist()

        # noinspection PyPropertyDefinition
        @property
        def email(self):
            self._does_not_exist()

        # noinspection PyPropertyDefinition
        @property
        def password(self):
            self._does_not_exist()

        @property
        def is_active(self):
            return False

        # noinspection PyPropertyDefinition
        @property
        def is_staff(self):
            self._does_not_exist()

        # noinspection PyPropertyDefinition
        @property
        def is_superuser(self):
            self._does_not_exist()

        # noinspection PyPropertyDefinition
        @property
        def id(self):
            self._does_not_exist()

        # noinspection PyPropertyDefinition, SpellCheckingInspection
        @property
        def socialaccount_set(self):
            self._does_not_exist()

        # noinspection PyPropertyDefinition
        @property
        def avatar_set(self):
            self._does_not_exist()

        # noinspection PyPropertyDefinition
        @property
        def last_login(self):
            self._does_not_exist()

        # noinspection PyPropertyDefinition
        @property
        def groups(self):
            self._does_not_exist()

        # noinspection PyPropertyDefinition
        @property
        def date_joined(self):
            self._does_not_exist()

        @property
        def is_anonymous(self):
            return True

        @property
        def is_authenticated(self):
            return False

        # noinspection PyPropertyDefinition, SpellCheckingInspection
        @property
        def emailaddress_set(self):
            self._does_not_exist()

        # noinspection PyPropertyDefinition, SpellCheckingInspection
        @property
        def staticdevice_set(self):
            self._does_not_exist()

        # noinspection PyPropertyDefinition, SpellCheckingInspection
        @property
        def totpdevice_set(self):
            self._does_not_exist()

        # noinspection PyPropertyDefinition
        @property
        def _meta(self):
            self._does_not_exist()

        # noinspection PyPropertyDefinition
        @property
        def _state(self):
            self._does_not_exist()

        @property
        def pk(self):
            return self.id

        # noinspection PyPropertyDefinition
        @property
        def user_permissions(self):
            self._does_not_exist()

        # noinspection PyPropertyDefinition
        @property
        def logentry_set(self):
            self._does_not_exist()

        @property
        def DoesNotExist(self):
            return BaseUser.DoesNotExist

        @property
        def MultipleObjectsReturned(self):
            return BaseUser.MultipleObjectsReturned

        @property
        def USERNAME_FIELD(self):
            return BaseUser.USERNAME_FIELD

        @property
        def EMAIL_FIELD(self):
            return BaseUser.EMAIL_FIELD

        @property
        def REQUIRED_FIELDS(self):
            return BaseUser.REQUIRED_FIELDS

        def __init__(self, profile: "Profile"):
            self.profile = profile

        def __str__(self):
            return "???"

        def __repr__(self):
            return "<Null_User: ???>"

        def __bool__(self):
            return False

        def __eq__(self, other):
            if not isinstance(other, type(self)):
                return False
            return True

        def __hash__(self) -> int:
            raise TypeError("Null_User instances have no key value, so are unhashable.")

        # noinspection PyUnusedLocal
        @username.setter
        def username(self, value: str):
            self._does_not_exist()

        # noinspection PyUnusedLocal
        @email.setter
        def email(self, value: str):
            self._does_not_exist()

        # noinspection PyUnusedLocal
        @password.setter
        def password(self, value: str):
            self._does_not_exist()

        @is_active.setter
        def is_active(self, value: bool) -> None:
            if value:
                raise BaseUser.DoesNotExist("No User object exists for this Profile, so is_active must be False.")

        # noinspection PyUnusedLocal
        @is_staff.setter
        def is_staff(self, value: bool):
            self._does_not_exist()

        # noinspection PyUnusedLocal
        @is_superuser.setter
        def is_superuser(self, value: bool):
            self._does_not_exist()

        # noinspection PyUnusedLocal
        @id.setter
        def id(self, value: int):
            self._does_not_exist()

        # noinspection SpellCheckingInspection
        @socialaccount_set.setter
        def socialaccount_set(self, value) -> None:
            raise TypeError("Direct assignment to the reverse side of a related set is prohibited. Use socialaccount_set.set() instead.")

        @avatar_set.setter
        def avatar_set(self, value) -> None:
            raise TypeError("Direct assignment to the reverse side of a related set is prohibited. Use avatar_set.set() instead.")

        # noinspection PyUnusedLocal
        @last_login.setter
        def last_login(self, value: datetime):
            self._does_not_exist()

        # noinspection PyUnusedLocal
        @groups.setter
        def groups(self, value):
            self._does_not_exist()

        # noinspection PyUnusedLocal
        @date_joined.setter
        def date_joined(self, value: datetime):
            self._does_not_exist()

        @is_anonymous.setter
        def is_anonymous(self, value: bool) -> None:
            if not value:
                raise BaseUser.DoesNotExist("No User object exists for this Profile, so is_anonymous must be True.")

        @is_authenticated.setter
        def is_authenticated(self, value: bool) -> None:
            if value:
                raise BaseUser.DoesNotExist("No User object exists for this Profile, so is_authenticated must be False.")

        # noinspection SpellCheckingInspection
        @emailaddress_set.setter
        def emailaddress_set(self, value) -> None:
            raise TypeError("Direct assignment to the reverse side of a related set is prohibited. Use emailaddress_set.set() instead.")

        # noinspection SpellCheckingInspection
        @staticdevice_set.setter
        def staticdevice_set(self, value) -> None:
            raise TypeError("Direct assignment to the reverse side of a related set is prohibited. Use staticdevice_set.set() instead.")

        # noinspection SpellCheckingInspection
        @totpdevice_set.setter
        def totpdevice_set(self, value) -> None:
            raise TypeError("Direct assignment to the reverse side of a related set is prohibited. Use totpdevice_set.set() instead.")

        # noinspection PyUnusedLocal
        @_meta.setter
        def _meta(self, value: Options):
            self._does_not_exist()

        # noinspection PyUnusedLocal
        @_state.setter
        def _state(self, value: models.base.ModelState):
            self._does_not_exist()

        @pk.setter
        def pk(self, value: int):
            self.id = value

        @user_permissions.setter
        def user_permissions(self, value) -> None:
            raise TypeError("Direct assignment to the reverse side of a related set is prohibited. Use user_permissions.set() instead.")

        @logentry_set.setter
        def logentry_set(self, value) -> None:
            raise TypeError("Direct assignment to the reverse side of a related set is prohibited. Use logentry_set.set() instead.")

        # noinspection PyUnusedLocal, PyUnusedLocal
        def save(self, force_insert=False, force_update=False, using: str = None, update_fields: Iterable[str] = None):
            self._does_not_exist()

        # noinspection PyUnusedLocal
        def delete(self, using: str = None, keep_parents=False):
            self._does_not_exist()

        def clean(self):
            self._does_not_exist()

        # noinspection PyUnusedLocal
        def clean_fields(self, exclude: Iterable[str] = None):
            self._does_not_exist()

        # noinspection PyUnusedLocal
        def full_clean(self, exclude: Iterable[str] = None, validate_unique=True, validate_constraints=True):
            self._does_not_exist()

        # noinspection PyUnusedLocal
        def validate_unique(self, exclude: Iterable[str] = None):
            self._does_not_exist()

        def get_constraints(self):
            raise BaseUser.DoesNotExist("Null_User object is cannot be instantiated, so has no fields, so has no constraints.")

        def validate_constraints(self, exclude: Iterable[str] = None):
            raise BaseUser.DoesNotExist("Null_User object is cannot be instantiated, so has no fields, so has no constraints.")

        # noinspection PyUnusedLocal
        def email_user(self, subject: str, message: str, from_email: str = None, **kwargs):
            self._does_not_exist()

        def get_username(self):
            return self.username

        def natural_key(self):
            return self.get_username(),

        # noinspection PyUnusedLocal
        def set_password(self, raw_password: str):
            self._does_not_exist()

        # noinspection PyUnusedLocal
        def check_password(self, raw_password: str):
            self._does_not_exist()

        # noinspection PyUnusedLocal
        def refresh_from_db(self, using: str = None, fields: Iterable[str] = None):
            self._does_not_exist()

        def set_unusable_password(self):
            raise BaseUser.DoesNotExist("No User object exists for this Profile, so an unusable password cannot be set.")

        # noinspection PyMethodMayBeStatic
        def has_usable_password(self):
            return False

        def get_session_auth_hash(self):
            raise BaseUser.DoesNotExist("No User object exists for this Profile, so there will be no sessions to get the auth hashes of.")

        def get_next_by_date_joined(self):
            self._does_not_exist()

        def get_previous_by_date_joined(self):
            self._does_not_exist()

        @classmethod
        def get_email_field_name(cls):  # TODO: Just do a call to the base user class (passing this class as an argument)
            try:
                return cls.EMAIL_FIELD
            except AttributeError:
                return "email"

        # noinspection SpellCheckingInspection
        @classmethod
        def normalize_username(cls, username):
            return (
                unicodedata.normalize("NFKC", username)
                if isinstance(username, str)
                else username
            )

        # noinspection PyUnusedLocal
        @classmethod
        def from_db(cls, db: str, field_names: Iterable[str], values: Iterable):
            cls._does_not_exist()

        @staticmethod
        def _does_not_exist():
            raise BaseUser.DoesNotExist("No User object found for this Profile.")

    def __str__(self):  # Returns the User's username if they are still visible, otherwise returns the crossed out username
        return self.string_when_visible(f"@{self.username}")

    @username.setter
    def username(self, value: str) -> None:
        if self.base_user is not None:  # TODO: Log warn attempted to be changed when no base_user
            if BaseUser.objects.filter(username__in=self.get_similar_usernames(value)).exists():
                raise ValueError(f"Username ({value}) is already in use.")
            self.base_user.username = BaseUser.normalize_username(value)
            self.base_user.full_clean()

    @email.setter
    def email(self, value: str) -> None:
        if self.base_user is not None:  # TODO: Log warn attempted to be changed when no base_user
            if EmailAddress.objects.filter(email=value).exclude(user=self.base_user).exists():
                raise ValueError(f"Email address ({value}) is already in use.")
            self.base_user.email = UserManager.normalize_email(value)

    @visible.setter
    def visible(self, value: bool):
        if self.base_user is not None and self.base_user.is_active != value:  # TODO: Log warn attempted to be changed when no base_user
            self.base_user.is_active = value
            self.base_user.full_clean()
            self.base_user.save()

    def delete(self, *args, **kwargs):  # TODO: prevent deletion (just set base user active to false)
        return super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()  # Perform full model validation before saving the object
        super().save(*args, **kwargs)

    @staticmethod
    def get_similar_usernames(username: str):  # Todo: get similar usernames & prevent new accounts with similar usernames
        return [username]


class Pulse(_User_Generated_Content_Model):  # TODO: disable the like & dislike buttons if profile already in set
    creator = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        verbose_name="Creator",
        related_name="pulses"
    )  # Provides a link to the Profile that created this Pulse
    liked_by = models.ManyToManyField(
        Profile,
        related_name="liked_pulses",
        blank=True
    )
    disliked_by = models.ManyToManyField(
        Profile,
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

        if not self.visible and Pulse.objects.get(id=self.id).visible:
            for reply in self.full_depth_replies:
                reply.update(base_save=True, clean=False, visible=False)

        elif self.visible and not Pulse.objects.get(id=self.id).visible:
            for reply in self.full_depth_replies:
                reply.update(base_save=True, clean=False, visible=True)

        super().save(*args, **kwargs)


class Reply(_User_Generated_Content_Model):  # TODO: disable the like & dislike buttons if profile already in set
    creator = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        verbose_name="Creator",
        related_name="replies"
    )  # Provides a link to the Profile that created this Reply
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
        Profile,
        related_name="liked_replies",
        blank=True
    )
    disliked_by = models.ManyToManyField(
        Profile,
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
        self.full_clean()

        self._original_pulse = self.original_pulse

        if not self.original_pulse.visible:  # TODO: make children invisible by recursion (make visible a private field with setter method)
            self.visible = False

        self.base_save(clean=False, *args, **kwargs)

    @staticmethod
    def _find_original_pulse(reply):
        if isinstance(reply.parent_object, Pulse):
            return reply.parent_object
        return Reply._find_original_pulse(reply.parent_object)


class Report(_Custom_Base_Model):  # TODO: create user privileges that can access reporting screens
    SPAM = "SPM"
    SEXUAL = "SEX"
    HATE = "HAT"
    VIOLENCE = "VIO"
    ILLEGAL_GOODS = "IGL"
    BULLYING = "BUL"
    INTELLECTUAL_PROPERTY = "INP"
    SELF_INJURY = "INJ"
    SCAM = "SCM"
    FALSE_INFO = "FLS"
    IN_PROGRESS = "PR"
    REJECTED = "RE"
    COMPLETED = "CM"
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
        Profile,
        on_delete=models.CASCADE,
        verbose_name="Reporter",
        related_name="reports"
    )
    assigned_staff = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        verbose_name="Assigned Staff Member",
        related_name="assigned_reports",
        limit_choices_to={"_base_user__is_staff": True},
        default=_choose_default_assigned_staff
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

    def __str__(self):
        return f"{self.reporter}, {self.get_category_display()}, {self.get_status_display()} (Assigned Staff Member - {self.assigned_staff})(For object - {self.parent_object})"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
