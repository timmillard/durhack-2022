from django.urls import path
from . import views

app_name = "catalog"



urlpatterns = [
    path('index/', views.Index.as_view(), name="index"),
    path('feed/', views.Feed.as_view(), name="feed"),
]
