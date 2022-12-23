"""
    Models in pulsifi application.
"""
from random import choice as random_choice

from django.conf import settings
from django.contrib.auth.models import User as BaseUser
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models


def _choose_default_assigned_staff():
    default_assigned_staff_QS = Profile.objects.filter(
        id=random_choice(
            Profile.objects.filter(_base_user__is_staff=True).values_list("id", flat=True)
        )
    )

    if default_assigned_staff_QS.exists():
        return default_assigned_staff_QS.get().id
    return None


class _Custom_Base_Model(models.Model):
    """
        Base model that provides extra utility methods for all other models to
        use.
    """

    class Meta:  # This class is abstract (only used for inheritance) so should not be able to be instantiated or have a table made for it in the database
        abstract = True

    def base_save(self, *args, **kwargs):
        pass

    def refresh_from_db(self, using=None, fields=None, deep=True):
        super().refresh_from_db(using=using, fields=fields)

        if deep:
            if fields:
                update_fields = [field for field in self._meta.get_fields(include_hidden=True) if field in fields and field.name != "+"]
            else:
                update_fields = [field for field in self._meta.get_fields() if field.name != "+"]

            updated_model = self._meta.model.objects.get(id=self.id)

            field: models.Field
            for field in update_fields:
                if not isinstance(field, models.ManyToManyField) and not isinstance(field, GenericRelation):
                    try:
                        setattr(self, field.name, getattr(updated_model, field.name))
                    except (AttributeError, TypeError, ValueError) as e:
                        pass  # TODO: use logging to log the error

    def update(self, commit=True, base_save=False, clean=True, **kwargs):
        """
            Change an object's values & save that object to the database all in
            one operation (based on Django's Queryset bulk update method).
        """

        for key, value in kwargs.items():  # Update the values of the kwargs provided
            setattr(self, key, value)

        if commit:  # Save the new object's state to the database as long as commit has been requested
            if base_save:
                self.base_save(clean)
            else:
                self.save()


class _Visible_Reportable_Model(_Custom_Base_Model):  # TODO: Make user visibility only based on is active flag
    """
        Base model that prevents objects from actually being deleted (making
        them invisible instead), as well as allowing all objects of this type
        to have reports made about them.
    """

    visible: bool
    reports = GenericRelation(
        "Report",
        content_type_field='_content_type',
        object_id_field='_object_id',
        related_query_name="reverse_parent_object",
        verbose_name="Reports"
    )  # Provides a link to the set of all Report objects that link to this object

    class Meta:  # This class is abstract (only used for inheritance) so should not be able to be instantiated or have a table made for it in the database
        abstract = True

    def string_when_visible(self, string: str):
        if self.visible:
            return string
        return "".join(f"{char}\u0336" for char in string)


class _User_Generated_Content_Model(_Visible_Reportable_Model):  # TODO: calculate time remaining based on engagement & creator follower count
    liked_by: models.ManyToManyField
    disliked_by: models.ManyToManyField
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


class Profile(_Visible_Reportable_Model):
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
        if self._base_user is None:
            return BaseUser(
                username="???",
                password="???",
                email="???",
                is_active=False,
                is_staff=None,
                is_superuser=None,
                first_name=None,
                last_name=None,
                date_joined=None
            )
        return self._base_user

    @property
    def username(self):  # Shortcut getter for the obfuscated field base_user.username
        return self.base_user.username

    @property
    def email(self):  # Shortcut getter for the obfuscated field base_user.email
        return self.base_user.email

    @property
    def date_joined(self):
        return self.base_user.date_joined

    @property
    def visible(self):
        if self.base_user.date_joined is None:
            return False
        return self.base_user.is_active

    class Meta:
        verbose_name = "User"

    def __str__(self):  # Returns the User's username if they are still visible, otherwise returns the crossed out username
        return self.string_when_visible(f"@{self.username}")

    @visible.setter
    def visible(self, value: bool):
        if self.base_user.date_joined is not None:
            self.base_user.is_active = value
            self.base_user.full_clean()
            self.base_user.save()

    def delete(self, *args, **kwargs):  # TODO: prevent deletion (just set base user active to false)
        return super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()  # Perform full model validation before saving the object
        super().save(*args, **kwargs)


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
    def all_replies(self):
        return Reply.objects.filter(_original_pulse=self)

    class Meta:
        verbose_name = "Pulse"

    def __str__(self):
        return f"{self.creator}, {self.string_when_visible(self.message[:settings.MESSAGE_DISPLAY_LENGTH])}"

    def save(self, *args, **kwargs):
        self.full_clean()

        if not self.visible and Pulse.objects.get(id=self.id).visible:
            for reply in self.all_replies:
                reply.update(base_save=True, clean=False, visible=False)

        elif self.visible and not Pulse.objects.get(id=self.id).visible:
            for reply in self.all_replies:
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

    def base_save(self, clean=True, *args, **kwargs):
        if clean:
            self.full_clean()
        _Visible_Reportable_Model.save(self, *args, **kwargs)

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
        (INTELLECTUAL_PROPERTY, "Intellectual property violation"),
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
