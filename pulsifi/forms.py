"""
    Forms in pulsifi application.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.models import User

from pulsifi.models import Post, Profile, Reply


class UserCreationForm(BaseUserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(
        max_length=Profile.meta.get_field("name").max_length
    )

    class Meta:
        model = User
        fields = (
            "name",
            "email",
            "username",
            "password1",
            "password2"
        )


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("creator", "message")


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ("creator", "message", "parent_object")


class ProfilePicForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("profile_pic",)


class BioForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("bio",)