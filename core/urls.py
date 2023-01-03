"""
    core URL Configuration.
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),  # NOTE: Check if the given URL matches one for the admin site
    path("accounts/", include("allauth.urls")),  # NOTE: Check if the given URL matches one for authentication/account management (only for temporary development use: eventually these views will be implemented within the pulsifi app)
    path("", include("pulsifi.urls")),  # NOTE: Check if the given URL matches one of the views in pulsifi app
    path("", RedirectView.as_view(pattern_name="pulsifi:home"), name="default")  # NOTE: If the empty URL is requested (just the domain) redirect to the pulsifi home view
]
