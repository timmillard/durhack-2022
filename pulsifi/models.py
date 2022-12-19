"""
    Models in pulsifi application.
"""
from typing import Callable

from django.conf import settings
from django.contrib.auth.models import User as BaseUser
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models


class _Custom_Base_Model(models.Model):
    """
        Base model that provides extra utility methods for all other models to
        use.
    """

    class Meta:  # This class is abstract (only used for inheritance) so should not be able to be instantiated or have a table made for it in the database
        abstract = True

    def update(self, commit=True, save_func: Callable[[], None] = None, **kwargs):
        """
            Change an object's values & save that object to the database all in
            one operation (based on Django's Queryset bulk update method).
        """

        if save_func is None:  # Use objects default save method if none is provided
            save_func = self.save

        for key, value in kwargs.items():  # Update the values of the kwargs provided
            setattr(self, key, value)
        if commit:  # Save the new object's state to the database as long as commit has been requested
            save_func()


class _Visible_Reportable_Model(_Custom_Base_Model):
    """
        Base model that prevents objects from actually being deleted (making
        them invisible instead), as well as allowing all objects of this type
        to have reports made about them.
    """

    class Meta:  # This class is abstract (only used for inheritance) so should not be able to be instantiated or have a table made for it in the database
        abstract = True

    visible = models.BooleanField("Visibility", default=True)
    reports = GenericRelation(
        "Report",
        content_type_field='_content_type',
        object_id_field='_object_id',
        related_query_name="reverse_parent_object",
        verbose_name="Reports"
    )  # Provides a link to the set of all Report objects that link to this object


class _User_Generated_Content_Model(_Visible_Reportable_Model):  # TODO: calculate time remaining based on engagement & creator follower count, check creating reply does not create pulse
    message = models.TextField("Message")
    _likes = models.PositiveIntegerField(
        "Number of Likes",
        default=0
    )
    _dislikes = models.PositiveIntegerField(
        "Number of Dislikes",
        default=0
    )
    replies = GenericRelation(
        "Reply",
        content_type_field='_content_type',
        object_id_field='_object_id',
        related_query_name="reverse_parent_object",
        verbose_name="Replies"
    )
    _date_time_created = models.DateTimeField(
        "Creation Date & Time",
        auto_now=True
    )

    @property
    def likes(self):  # TODO: prevent users from increasing the time by liking then unliking then reliking
        return self._likes

    @property
    def dislikes(self):
        return self._dislikes

    @property
    def date_time_created(self):
        return self._date_time_created

    class Meta:  # This class is abstract (only used for inheritance) so should not be able to be instantiated or have a table made for it in the database
        abstract = True

    def __str__(self):
        if self.visible:
            return self.message[:settings.MESSAGE_DISPLAY_LENGTH]
        return "".join(letter + "\u0336" for letter in self.message[:settings.MESSAGE_DISPLAY_LENGTH])

    def delete(self, *args, **kwargs):  # TODO: prevent deletion (just set visibility to false)
        return super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.visible and Pulse.objects.get(id=self.id).visible:
            for reply in Reply.objects.filter(_original_pulse=self):
                reply.update(save_func=reply.super_save, visible=False)
        super().save(*args, **kwargs)

    def like(self):  # TODO: add Pulse to profile's like list
        self.update(_likes=self.likes + 1)

    def dislike(self):  # TODO: add Pulse to profile's dislike list
        self.update(_dislikes=self.dislikes + 1)


class Profile(_Visible_Reportable_Model):  # TODO: store which pulses a user has liked & disliked (in order to disable the correct buttons)
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
        return self._base_user

    @property
    def username(self):  # Shortcut getter for the obfuscated field base_user.username
        return self.base_user.username

    @property
    def email(self):  # Shortcut getter for the obfuscated field base_user.email
        return self.base_user.email

    class Meta:
        verbose_name = "User"

    def __str__(self):  # Returns the User's username if they are still visible, otherwise returns the crossed out username
        return_value = f"@{self.username}"
        if self.visible:
            return return_value
        return "".join(letter + "\u0336" for letter in return_value)

    def delete(self, *args, **kwargs):  # TODO: prevent deletion (just set visibility to false)
        return super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.base_user:
            self.visible = False
        else:
            if not self.base_user.is_active:  # Makes Profile invisible if the underlying User object has been deactivated
                self.visible = False
            elif not self.visible:  # Deactivates the underlying User object if Profile has been made invisible
                self.base_user.is_active = False
                self.base_user.save()
            # TODO: make invisible if _base_user is null

        self.full_clean()  # Perform full model validation before saving the object
        super().save(*args, **kwargs)


class Pulse(_User_Generated_Content_Model):
    creator = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        verbose_name="Creator",
        related_name="pulses"
    )  # Provides a link to the Profile that created this Pulse

    class Meta:
        verbose_name = "Pulse"

    def __str__(self):
        if self.visible:
            return f"{self.creator}, {self.message[:settings.MESSAGE_DISPLAY_LENGTH]}"
        return f"{self.creator}, " + "".join(letter + "\u0336" for letter in self.message[:settings.MESSAGE_DISPLAY_LENGTH])


class Reply(_User_Generated_Content_Model):
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

    @property
    def original_pulse(self):
        return self._original_pulse

    class Meta:
        verbose_name = "Reply"

    def __str__(self):
        if self.visible:
            return f"{self.creator}, {self.message[:settings.MESSAGE_DISPLAY_LENGTH]} (For object - {self.parent_object})"
        return f"{self.creator}, " + "".join(letter + "\u0336" for letter in self.message[:settings.MESSAGE_DISPLAY_LENGTH]) + f" (For object - {self.parent_object})"

    def save(self, *args, **kwargs):
        try:
            self.original_pulse()
        except Pulse.DoesNotExist:
            self._original_pulse = self._find_original_pulse(self)

        if not self.original_pulse.visible:
            self.visible = False

        self.super_save(*args, **kwargs)

    def super_save(self, *args, **kwargs):
        self.full_clean()
        _Visible_Reportable_Model.save(self, *args, **kwargs)

    @staticmethod
    def _find_original_pulse(reply):
        if isinstance(reply.parent_object, Pulse):
            return reply.parent_object
        return Reply._find_original_pulse(reply.parent_object)


class Report(_Custom_Base_Model):  # TODO: create user privileges that can access reporting screens, add extra solved_by field linking user model
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
    CONFIRMED = "CN"
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
        (CONFIRMED, "Confirmed")
    ]

    _content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    _object_id = models.PositiveIntegerField()
    parent_object = GenericForeignKey(ct_field="_content_type", fk_field="_object_id")
    reporter = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        verbose_name="Reporter"
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
        choices=status_choices
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
        return f"{self.reporter}, {self.get_category_display()}, {self.get_status_display()} (For object - {self.parent_object})"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)