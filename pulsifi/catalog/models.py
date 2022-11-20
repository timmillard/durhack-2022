from django.db import models
from django.contrib.auth.models import User
from django.db.models import F
# Create your models here.


class Profile(models.Model):
    _base_user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(
        "bio",
        max_length=200,
        blank=True,
        null=True
    )
    profile_pic = models.ImageField(upload_to="profile_pics", blank=True, null=True)
    
    name = models.CharField("Name", max_length=30)


    @property
    def base_user(self):
        return self._base_user

    class Meta:
        verbose_name = "User"

    def __str__(self):
        return self._base_user.username

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args,**kwargs)

class Post(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date_time_created = models.DateTimeField(
        "Post Creation Time",
        auto_now=True
    )
    message = models.TextField("Post Message")
    likes = models.PositiveIntegerField(
        "Number of Likes",
        default=0
    )
    dislikes = models.PositiveIntegerField(
        "Number of Dislikes",
        default=0
    )

    @property
    def date_time_created(self):
        return self._date_time_created

    class Meta:
        verbose_name = "Post"

    def __str__(self):
        return self.message

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def like_post(self):
        self.update(likes=F("likes")+1)
        self.save()

    def dislike_post(self):
        self.update(likes=F("dislikes")+1)
        self.save()

    def delete(self):
        self.delete()
        self.save()