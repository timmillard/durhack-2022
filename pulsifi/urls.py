"""
    pulsifi URL configuration.
"""

from django import urls as django_urls

from pulsifi import views

app_name = "pulsifi"

urlpatterns: list[django_urls.URLPattern] = [
    django_urls.path("", views.Home_View.as_view(), name="home"),
    django_urls.path("feed/", views.Feed_View.as_view(), name="feed"),
    # TODO: user search url, leaderboard url
    django_urls.path("user/", views.Self_Account_View.as_view(), name="self_account"),
    django_urls.path(
        "user/@<str:username>/",
        views.Specific_Account_View.as_view(),
        name="specific_account"
    ),
    django_urls.path("following/", views.Following_View.as_view(), name="following"),
    django_urls.path("followers/", views.Followers_View.as_view(), name="followers"),
    django_urls.path("signup/", views.Signup_POST_View.as_view(), name="signup_POST"),
    django_urls.path("login/", views.Login_POST_View.as_view(), name="login_POST")
    # TODO: password change view, confirm email view, manage emails view, password set after not having one because of social login view, forgotten password reset view, forgotten password reset success view, Popup for are you sure you want to logout
]
