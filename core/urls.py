"""
    core URL Configuration.
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
    path('avatar/', include("avatar.urls")),
    path('admin/doc/', include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),  # NOTE: Check if the given URL matches one for authentication/account management (only for temporary development use: eventually these views will be implemented within the pulsifi app)
    path("", include("pulsifi.urls")),
    path("", RedirectView.as_view(pattern_name="pulsifi:home"), name="default")
]
