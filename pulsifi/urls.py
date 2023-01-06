"""
    pulsifi URL configuration.
"""

from django.urls import path
from django.views.generic.base import RedirectView

from . import views

app_name = "pulsifi"

urlpatterns = [
    path("", views.Home_View.as_view(), name="home"),
    path(
        "index.html",
        RedirectView.as_view(pattern_name="pulsifi:home"),
        name="index_html_redirect"
    ),
    path(
        "index/",
        RedirectView.as_view(pattern_name="pulsifi:home"),
        name="index_redirect"
    ),
    path(
        "home/",
        RedirectView.as_view(pattern_name="pulsifi:home"),
        name="home_redirect"
    ),
    path("feed/", views.Feed_View.as_view(), name="feed"),
    # TODO: user search url, leaderboard url
    path("user/", views.Self_Account_View.as_view(), name="self_account"),
    path(
        "user/@<str:username>",
        views.Specific_Account_View.as_view(),
        name="specific_account"
    ),
    path("create-new-pulse", views.Create_Pulse_View.as_view(), name="create_pulse"),
    path("signup/", views.Signup_View.as_view(), name="signup")
    # TODO: logout view, password change view, confirm email view, manage emails view, password set after not having one because of social login view, forgotten password reset view, forgotten password reset success view
]
