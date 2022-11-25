"""
    pulsifi URL configuration.
"""

from django.urls import path

from . import views

app_name = "pulsifi"

urlpatterns = [
    path("index/", views.Index_view.as_view(), name="index"),
    path("feed/", views.Feed_view.as_view(), name="feed"),
    path("home/", views.Home_view.as_view(), name="home"),
    path("profile/", views.Profile_view.as_view(), name="profile"),
    path("profile/1", views.Profile1_view.as_view(), name="profile1"),
    path("profile/2", views.Profile2_view.as_view(), name="profile2"),
    path("sign_up/", views.SignUp_view.as_view(), name="sign_up"),
]