"""
    Models in pulsifi application.
"""

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Custom_Model(models.Model):
    class Meta:
        abstract = True

    def update(self, commit=True, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if commit:
            self.save()


class Profile(Custom_Model):
    _base_user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField("Name", max_length=30)
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
        return f"@{self.base_user.username}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Pulse(Custom_Model):  # TODO: calculate time remaining based on likes & creator follower count
    creator = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        verbose_name="Creator"
    )
    message = models.TextField("Message")
    visible = models.BooleanField("Visibility", default=True)
    _likes = models.PositiveIntegerField(
        "Number of Likes",
        default=0
    )
    _dislikes = models.PositiveIntegerField(
        "Number of Dislikes",
        default=0
    )
    _date_time_created = models.DateTimeField(
       "Creation Date & Time",
       auto_now=True
    )
    replies = GenericRelation(
        "Reply",
        content_type_field='_content_type',
        object_id_field='_object_id',
        related_query_name="reverse_parent_object",
        verbose_name="Replies"
    )

    @property
    def date_time_created(self):
        return self._date_time_created

    @property
    def likes(self):
        return self._likes

    @property
    def dislikes(self):
        return self._dislikes

    class Meta:
        verbose_name = "Pulse"

    def __str__(self):
        return f"{self.creator}, {self.message[:settings.MESSAGE_DISPLAY_LENGTH]}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def like(self):
        self.update(_likes=self.likes + 1)

    def dislike(self):
        self.update(_dislikes=self.dislikes + 1)

class Reply(Pulse):
    _content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    _object_id = models.PositiveIntegerField()
    parent_object = GenericForeignKey(ct_field="_content_type", fk_field="_object_id")

    class Meta:
        verbose_name = "Reply"

    def __str__(self):
        return f"{self.creator}, {self.message[:settings.MESSAGE_DISPLAY_LENGTH]} (For object - {self.parent_object})"