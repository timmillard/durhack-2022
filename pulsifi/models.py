"""
    Models in pulsifi application.
"""

from django.conf import settings
from django.contrib.auth.models import User as BaseUser
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Custom_Base_Model(models.Model):
    class Meta:
        abstract = True

    def update(self, commit=True, save_func=None, **kwargs):
        if save_func is None:
            save_func = self.save

        for key, value in kwargs.items():
            setattr(self, key, value)
        if commit:
            save_func()


class Visible_Model(Custom_Base_Model):
    visible = models.BooleanField("Visibility", default=True)
    _report = GenericRelation(
        "Report",
        content_type_field='_content_type',
        object_id_field='_object_id',
        related_query_name="reverse_parent_object"
    )

    @property
    def report(self):
        return self._report.first()


class Profile(Visible_Model):  # TODO: store which pulses a user has liked (in order to disable the correct buttons)
    _base_user = models.OneToOneField(BaseUser, null=True, on_delete=models.SET_NULL)
    name = models.CharField("Name", max_length=30)  # TODO: use django all-auth to store this
    bio = models.TextField(
        "Bio",
        max_length=200,
        blank=True,
        null=True
    )
    profile_pic = models.ImageField(
        "Profile Picture",
        upload_to="profile_pic",
        blank=True,
        null=True
    )
    following = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="followers",
        blank=True
    )

    @property
    def base_user(self):
        return self._base_user

    class Meta:
        verbose_name = "User"

    def __str__(self):
        return_value = f"@{self.base_user.username}"
        if self.visible:
            return return_value
        return "".join(letter + "\u0336" for letter in return_value)

    def delete(self, *args, **kwargs):  # TODO: prevent deletion (just set visibility to false)
        return super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.base_user.is_active:
            self.visible = False
        elif not self.visible:
            self.base_user.is_active = False
            self.base_user.save()

        self.full_clean()
        super().save(*args, **kwargs)


class Pulse(Visible_Model):  # TODO: calculate time remaining based on likes & creator follower count
    creator = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        verbose_name="Creator",
        related_name="pulses_and_replies"
    )
    message = models.TextField("Message")
    unlisted = models.BooleanField("Unlisted", default=False)
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

    class Meta:
        verbose_name = "Pulse"

    def __str__(self):
        if self.visible:
            return f"{self.creator}, {self.message[:settings.MESSAGE_DISPLAY_LENGTH]}"
        return f"{self.creator}, " + "".join(letter + "\u0336" for letter in self.message[:settings.MESSAGE_DISPLAY_LENGTH])

    def delete(self, *args, **kwargs):  # TODO: prevent deletion (just set visibility to false)
        return super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.visible and Pulse.objects.get(id=self.id).visible:
            for reply in Reply.objects.filter(_original_pulse=self):
                reply.update(save_func=reply.super_save, visible=False)
        super().save(*args, **kwargs)

    def like(self):
        self.update(_likes=self.likes + 1)

    def dislike(self):
        self.update(_dislikes=self.dislikes + 1)

class Reply(Pulse):
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
        if self.original_pulse is None:
            self._original_pulse = self._find_original_pulse(self)

        if not self.original_pulse.visible:
            self.visible = False

        self.super_save(self, *args, **kwargs)

    def super_save(self, *args, **kwargs):
        self.full_clean()
        Visible_Model.save(self, *args, **kwargs)

    @staticmethod
    def _find_original_pulse(reply):
        if isinstance(reply.parent_object, Pulse):
            return reply.parent_object
        return Reply._find_original_pulse(reply.parent_object)

class Report(Custom_Base_Model):
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
    RESOLVED = "RE"
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
    status_choices = [(IN_PROGRESS, "In progress"), (RESOLVED, "Resolved")]

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