"""
    Utility functions within core app.
"""

from typing import Collection

from django import urls as django_urls
from django.http import QueryDict
from django.utils.functional import lazy


def reverse_url_with_get_params(*args, **kwargs) -> str:
    """
        Returns a URL from the given view name, with the given get_params
        appended to the end.
    """

    get_params: dict[str, ...] = kwargs.pop("get_params", {})
    url: str = django_urls.reverse(*args, **kwargs)
    if not get_params:
        return url

    qdict = QueryDict("", mutable=True)
    for key, val in get_params.items():
        if isinstance(val, Collection) and not isinstance(val, str):
            qdict.setlist(key, list(val))
        else:
            qdict[key] = val

    return url + "?" + qdict.urlencode()


reverse_url_with_get_params_lazy = lazy(reverse_url_with_get_params, str)
"""
    A lazily evaluated version of the reverse_url_with_get_params function,
    that returns a URL from the given view name, with the given get_params
    appended to the end.
"""
