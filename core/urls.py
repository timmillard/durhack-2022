"""
    core URL Configuration.
"""

from django.contrib import admin
from django.urls import include, path, reverse
from django.views.generic.base import RedirectView


class Admin_Docs_Redirect_View(RedirectView):
    """
        Helper redirect view for the /docs/ url to /doc/ (with any included
        subpath).
    """

    def get_redirect_url(self, *args, **kwargs):
        """
            Return the URL redirect to. Keyword arguments from the URL pattern
            match generating the redirect request are provided as kwargs to
            this method. Also adds a possible subpath to the end of the
            redirected URL.
        """

        subpath = ""
        if "subpath" in self.kwargs:
            subpath = self.kwargs.pop("subpath")
            kwargs.pop("subpath")

        # noinspection SpellCheckingInspection
        url = reverse("django-admindocs-docroot", args=args, kwargs=kwargs) + subpath

        args = self.request.META.get("QUERY_STRING", "")
        if args and self.query_string:
            url = f"{url}?{args}"

        return url


urlpatterns = [
    path("avatar/", include("avatar.urls")),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/docs/", Admin_Docs_Redirect_View.as_view(), name="admindocs_redirect"),
    path("admin/docs/<path:subpath>", Admin_Docs_Redirect_View.as_view(), name="admindocs_redirect_with_subpath"),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),  # NOTE: Check if the given URL matches one for authentication/account management (only for temporary development use: eventually these views will be implemented within the pulsifi app)
    path("", include("pulsifi.urls")),
    path("", RedirectView.as_view(pattern_name="pulsifi:home"), name="default")
]
