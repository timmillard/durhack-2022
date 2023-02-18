"""
    pulsifi URL configuration.
"""
from typing import Sequence

from django.urls import URLPattern, path

from . import views

app_name = "pulsifi"

urlpatterns: Sequence[URLPattern] = [
    path("", views.Home_View.as_view(), name="home"),
    path("feed/", views.Feed_View.as_view(), name="feed"),
    # TODO: user search url, leaderboard url
    path("user/", views.Self_Account_View.as_view(), name="self_account"),
    path(
        "user/@<str:username>",
        views.Specific_Account_View.as_view(),
        name="specific_account"
    ),
    path("create-new-pulse", views.Create_Pulse_View.as_view(), name="create_pulse"),
    path("signup/", views.Signup_POST_View.as_view(), name="signup_POST"),
    path("login/", views.Login_POST_View.as_view(), name="login_POST")
    # TODO: password change view, confirm email view, manage emails view, password set after not having one because of social login view, forgotten password reset view, forgotten password reset success view, Popup for are you sure you want to logout
]
