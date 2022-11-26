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
    path("profile/", views.Self_Profile_View.as_view(), name="self_profile"),
    path(
        "profile/<int:profile_id>",
        views.ID_Profile_View.as_view(),
        name="id_profile"
    ),
    path("post/create", views.Create_Post_View.as_view(), name="create_post"),
    path("signup/", views.Signup_View.as_view(), name="signup")
]