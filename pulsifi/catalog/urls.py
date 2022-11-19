from django.urls import path
from . import views

app_name = "catalog"



urlpatterns = [
    path('index/', views.Index.as_view(), name="index"),
    path('feed/', views.Feed.as_view(), name="feed"),
    path('home/', views.Home.as_view(), name="home"),
    path('profile/', views.Profile.as_view(), name="profile"),
    path('profile/1', views.Profile1.as_view(), name="profile1"),
    path('profile/2', views.Profile2.as_view(), name="profile2"),
]
