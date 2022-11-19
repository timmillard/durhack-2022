from django.db import models
from django.contrib.auth.models import User
from django.db.models import F
# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(
        "bio",
        max_length=500,
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
    date_time_created = models.DateTimeField(
        auto_now=True
    )
    likes = models.PositiveIntegerField(
        default=0
    )
def like_post(self):
    self.update(likes=F("likes")+1)
    