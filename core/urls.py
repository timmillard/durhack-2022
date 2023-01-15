"""
    core URL Configuration.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
    path(
        "admin/password-reset/",
        auth_views.PasswordResetView.as_view(),
        name="admin_password_reset",
    ),
    path(
        "admin/password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="admin_password_reset_done",
    ),
    path(
        "admin/password-reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="admin_password_reset_confirm",
    ),
    path(
        "admin/password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(),
        name='admin_password_reset_complete',
    ),
    path("admin/", admin.site.urls),  # NOTE: Check if the given URL matches one for the admin site
    path("accounts/", include("allauth.urls")),  # NOTE: Check if the given URL matches one for authentication/account management (only for temporary development use: eventually these views will be implemented within the pulsifi app)
    path("", include("pulsifi.urls")),  # NOTE: Check if the given URL matches one of the views in pulsifi app
    path("", RedirectView.as_view(pattern_name="pulsifi:home"), name="default")  # NOTE: If the empty URL is requested (just the domain) redirect to the pulsifi home view
]
