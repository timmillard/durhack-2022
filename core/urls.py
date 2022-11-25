"""
    core URL Configuration.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("pulsifi.urls")),
    path('', RedirectView.as_view(pattern_name="pulsifi:home"), name="default")
]