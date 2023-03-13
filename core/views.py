"""
    Views in core app.
"""

from django import urls as django_urls
from django.views.generic import RedirectView


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
        url = django_urls.reverse("django-admindocs-docroot", args=args, kwargs=kwargs) + subpath

        args = self.request.META.get("QUERY_STRING", "")
        if args and self.query_string:
            url = f"{url}?{args}"

        return url
