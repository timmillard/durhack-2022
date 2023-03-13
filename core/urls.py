"""
    core URL Configuration.
"""

from django import urls as django_urls
from django.conf import settings
from django.conf.urls import static
from django.contrib import admin
from django.views.generic.base import RedirectView

from core.views import Admin_Docs_Redirect_View

_urlpatterns_list: list[django_urls.URLPattern] = [
    django_urls.path("avatar/", django_urls.include("avatar.urls")),
    django_urls.path(
        "admin/doc/",
        django_urls.include("django.contrib.admindocs.urls")
    ),
    django_urls.path(
        "admin/docs/",
        Admin_Docs_Redirect_View.as_view(),
        name="admindocs_redirect"
    ),
    django_urls.path(
        "admin/docs/<path:subpath>",
        Admin_Docs_Redirect_View.as_view(),
        name="admindocs_redirect_with_subpath"
    ),
    django_urls.path("admin/", admin.site.urls),
    django_urls.path(
        "accounts/",
        django_urls.include("allauth.urls")
    ),  # NOTE: Check if the given URL matches one for authentication/account management (only for temporary development use: eventually these views will be implemented within the pulsifi app)
    django_urls.path("", django_urls.include("pulsifi.urls")),
    django_urls.path(
        "",
        RedirectView.as_view(pattern_name="pulsifi:home"),
        name="default"
    )
]

urlpatterns: list[django_urls.URLPattern] = _urlpatterns_list + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
