from django.db import models
from django.contrib.auth.models import User
from django.db.models import F
# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(
        "bio",
        max_length=200,
        blank=True,
    )
    profile_pic = models.ImageField(upload_to="profile_pics")
    

    class Meta:
        verbose_name = "User"

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args,**kwargs)

class Post(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date_time_created = models.DateTimeField(
        auto_now=True
    )
    message = models.TextField(
        "message",
        max_length=350,
        blank=True,
    )
    likes = models.PositiveIntegerField(
        default=0
    )
    dislikes = models.PositiveIntegerField(
        default=0
    )
    def like_post(self):
        self.update(likes=F("likes")+1)
    def dislike_post(self):
        self.update(likes=F("dislikes")+1)
    def delete(self):
        self.delete()